


from typing import Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.package import Package, StatusEnum
from app.models.most_visited import MostVisited

from app.schemas.package import (
    PackageCreate,
    PackageUpdate,
)

from app.core.redis_client import (
    cache_get,
    cache_set,
    cache_delete_pattern,
)

from app.core.slugify import unique_slug

CACHE_PREFIX = "packages"


# ============================================================
# SERIALIZATION
# ============================================================


def _serialize(pkg: Package) -> dict:
    """
    Convert a Package SQLAlchemy object into a JSON-safe dictionary.
    """

    return {
        "id": pkg.id,
        "title": pkg.title,
        "slug": pkg.slug,
        # Existing display/compatibility field
        "destination": pkg.destination,
        # NEW: actual destination relationship
        "destination_id": pkg.destination_id,
        # ----------------------------------------------------
        # Package classification
        # ----------------------------------------------------
        "package_type": (pkg.package_type.value if pkg.package_type else None),
        # ----------------------------------------------------
        # Admin-controlled display order
        # ----------------------------------------------------
        "display_order": pkg.display_order,
        # ----------------------------------------------------
        # Discovery / visibility flags
        # ----------------------------------------------------
        "is_popular": bool(pkg.is_popular),
        "is_recommended": bool(pkg.is_recommended),
        "is_trending": bool(pkg.is_trending),
        "is_featured": bool(pkg.is_featured),
        "is_new": bool(pkg.is_new),
        "is_most_visited": bool(pkg.is_most_visited),
        # ----------------------------------------------------
        # Pricing & duration
        # ----------------------------------------------------
        "price": str(pkg.price),
        "duration_days": pkg.duration_days,
        "duration_nights": pkg.duration_nights,
        # ----------------------------------------------------
        # Description
        # ----------------------------------------------------
        "description": pkg.description,
        # ----------------------------------------------------
        # Images & itinerary
        # ----------------------------------------------------
        "images": pkg.images or [],
        "itinerary": pkg.itinerary or [],
        # ----------------------------------------------------
        # Package details
        # ----------------------------------------------------
        "facilities": pkg.facilities or [],
        "inclusions": pkg.inclusions or [],
        "exclusions": pkg.exclusions or [],
        # ----------------------------------------------------
        # Package policies
        # ----------------------------------------------------
        "terms_and_conditions": pkg.terms_and_conditions,
        "cancellation_policy": pkg.cancellation_policy,
        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------
        "status": (pkg.status.value if pkg.status else None),
        # ----------------------------------------------------
        # Metadata
        # ----------------------------------------------------
        "created_by": pkg.created_by,
        "created_at": (pkg.created_at.isoformat() if pkg.created_at else None),
        "updated_at": (pkg.updated_at.isoformat() if pkg.updated_at else None),
    }


# ============================================================
# DESTINATION VALIDATION
# ============================================================


def _get_destination(
    db: Session,
    destination_id: int,
) -> MostVisited:
    """
    Find the destination referenced by destination_id.

    Only published destinations can be assigned to packages.
    """

    destination = (
        db.query(MostVisited)
        .filter(
            MostVisited.id == destination_id,
            MostVisited.status == "published",
        )
        .first()
    )

    if not destination:
        raise HTTPException(
            status_code=400,
            detail="Invalid or unpublished destination",
        )

    return destination


# ============================================================
# DISPLAY ORDER
# ============================================================


def _place_in_order(
    db: Session,
    pkg: Package,
    new_order: Optional[int],
    exclude_id: Optional[int] = None,
) -> None:
    """
    Put `pkg` at position `new_order` and renumber ALL packages 1..n.

    - Fixes duplicate / zero display_order values automatically.
    - new_order empty / 0 / beyond the end -> the package goes last.
    - exclude_id: pass pkg.id when the package already exists in the DB,
      so it is not counted twice.

    Examples (unique orders 1..5):
        move 5 -> 2 : old 2, 3, 4 become 3, 4, 5
        move 2 -> 5 : old 3, 4, 5 become 2, 3, 4

    Call this BEFORE db.commit() so the reorder and the package
    save happen in one transaction.
    """

    query = db.query(Package)

    if exclude_id is not None:
        query = query.filter(Package.id != exclude_id)

    others = query.order_by(
        Package.display_order.asc(),
        Package.id.asc(),
    ).all()

    total = len(others) + 1

    if not new_order:
        position = total
    else:
        position = max(1, min(int(new_order), total))

    others.insert(position - 1, pkg)

    for index, item in enumerate(others, start=1):
        if item.display_order != index:
            item.display_order = index


def _normalize_display_orders(db: Session) -> None:
    """
    Renumber every package 1..n (used after delete).
    """

    packages = (
        db.query(Package)
        .order_by(
            Package.display_order.asc(),
            Package.id.asc(),
        )
        .all()
    )

    for index, item in enumerate(packages, start=1):
        if item.display_order != index:
            item.display_order = index


# ============================================================
# CACHE
# ============================================================


def _invalidate_cache() -> None:
    """
    Wipe every cached packages:* key.
    """

    cache_delete_pattern(f"{CACHE_PREFIX}:*")


def _invalidate_destination_cache() -> None:
    """
    Packages are included inside destination responses.

    Therefore, whenever a package changes, cached
    MostVisited/destination responses must also be cleared.
    """

    cache_delete_pattern("most_visited:*")


def _invalidate_all_related_cache() -> None:
    """
    Clear both package and destination caches.
    """

    _invalidate_cache()
    _invalidate_destination_cache()


# ============================================================
# PUBLIC — GET ALL PUBLISHED PACKAGES
# ============================================================


def get_published_packages(
    db: Session,
    collection: Optional[str] = None,
) -> list[dict]:
    """
    Public endpoint.

    Returns only published packages.

    Optional discovery collections:

        /packages
        /packages?collection=popular
        /packages?collection=recommended
        /packages?collection=trending
        /packages?collection=featured
        /packages?collection=new
        /packages?collection=most_visited
    """

    collection = collection.strip().lower() if collection else None

    collection_filters = {
        "popular": Package.is_popular,
        "recommended": Package.is_recommended,
        "trending": Package.is_trending,
        "featured": Package.is_featured,
        "new": Package.is_new,
        "most_visited": Package.is_most_visited,
    }

    if collection and collection not in collection_filters:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid collection. "
                "Allowed values: "
                "popular, recommended, trending, "
                "featured, new, most_visited."
            ),
        )

    if collection:
        cache_key = f"{CACHE_PREFIX}:" f"published:" f"{collection}"
    else:
        cache_key = f"{CACHE_PREFIX}:published"

    cached = cache_get(cache_key)

    if cached is not None:
        return cached

    query = db.query(Package).filter(Package.status == StatusEnum.published)

    if collection:
        query = query.filter(collection_filters[collection].is_(True))

    packages = query.order_by(
        Package.display_order.asc(),
        Package.created_at.desc(),
    ).all()

    data = [_serialize(package) for package in packages]

    cache_set(cache_key, data)

    return data


# ============================================================
# PUBLIC / ADMIN — GET PACKAGE BY ID
# ============================================================


def get_package_by_id(
    db: Session,
    package_id: int,
) -> dict:
    """
    Get a package by ID.

    This function does not restrict status, so it can return
    both draft and published packages.

    Public routes should preferably use get_package_by_slug().
    """

    cache_key = f"{CACHE_PREFIX}:id:{package_id}"

    cached = cache_get(cache_key)

    if cached is not None:
        return cached

    pkg = db.query(Package).filter(Package.id == package_id).first()

    if not pkg:
        raise HTTPException(
            status_code=404,
            detail="Package not found",
        )

    data = _serialize(pkg)

    cache_set(cache_key, data)

    return data


# ============================================================
# PUBLIC — GET PACKAGE BY SLUG
# ============================================================


def get_package_by_slug(
    db: Session,
    slug: str,
) -> dict:
    """
    Get a published package by slug.
    Used by the public package detail page.
    """

    cache_key = f"{CACHE_PREFIX}:slug:{slug}"

    cached = cache_get(cache_key)

    if cached is not None:
        return cached

    pkg = (
        db.query(Package)
        .filter(
            Package.slug == slug,
            Package.status == StatusEnum.published,
        )
        .first()
    )

    if not pkg:
        raise HTTPException(
            status_code=404,
            detail="Package not found",
        )

    data = _serialize(pkg)

    cache_set(cache_key, data)

    return data


# ============================================================
# ADMIN — GET ALL PACKAGES
# ============================================================


def get_all_packages_admin(
    db: Session,
) -> list[dict]:
    """
    Admin/creator view.

    Includes:
    - draft packages
    - published packages
    """

    packages = (
        db.query(Package)
        .order_by(
            Package.display_order.asc(),
            Package.created_at.desc(),
        )
        .all()
    )

    return [_serialize(package) for package in packages]


# ============================================================
# CREATE PACKAGE
# ============================================================


def create_package(
    db: Session,
    payload: PackageCreate,
    user_id: int,
) -> Package:
    """
    Create a new package.

    destination_id is the authoritative destination relationship.
    The legacy destination text field is synchronized automatically.

    display_order: the package is inserted at the requested position
    and all packages are renumbered 1..n. Empty / 0 adds it last.
    """

    # --------------------------------------------------------
    # Validate destination
    # --------------------------------------------------------

    destination = _get_destination(
        db,
        payload.destination_id,
    )

    # --------------------------------------------------------
    # Generate unique slug
    # --------------------------------------------------------

    slug = unique_slug(
        db,
        Package,
        payload.title,
    )

    # --------------------------------------------------------
    # Convert payload
    # --------------------------------------------------------

    package_data = payload.model_dump(
        exclude={
            "images",
            "itinerary",
            "destination",
        }
    )

    # Requested position (handled by _place_in_order below)
    requested_order = package_data.pop("display_order", None)

    # destination_id is authoritative from the resolved destination
    package_data.pop("destination_id", None)

    # --------------------------------------------------------
    # Create package
    # --------------------------------------------------------

    pkg = Package(
        **package_data,
        # temporary value, set properly by _place_in_order
        display_order=0,
        # destination_id is authoritative
        destination_id=destination.id,
        # Keep old destination column synchronized
        destination=destination.place_name,
        # Convert Pydantic image objects
        images=[img.model_dump() for img in payload.images],
        # Convert itinerary objects
        itinerary=[item.model_dump() for item in payload.itinerary],
        slug=slug,
        created_by=user_id,
    )

    # --------------------------------------------------------
    # Display order
    # Must run BEFORE db.add(pkg) so the new package is not
    # already part of the query result.
    # --------------------------------------------------------

    _place_in_order(
        db,
        pkg,
        requested_order,
    )

    # --------------------------------------------------------
    # Save (reorder + insert in one transaction)
    # --------------------------------------------------------

    db.add(pkg)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(pkg)

    # --------------------------------------------------------
    # Clear related caches
    # --------------------------------------------------------

    _invalidate_all_related_cache()

    return pkg


# ============================================================
# UPDATE PACKAGE
# ============================================================


def update_package(
    db: Session,
    package_id: int,
    payload: PackageUpdate,
) -> Package:
    """
    Update an existing package.

    destination_id is the authoritative destination relationship.

    display_order: when provided, the package is moved to that
    position and all packages are renumbered 1..n, so no two
    packages ever share the same order.
    """

    # --------------------------------------------------------
    # Find package
    # --------------------------------------------------------

    pkg = db.query(Package).filter(Package.id == package_id).first()

    if not pkg:
        raise HTTPException(
            status_code=404,
            detail="Package not found",
        )

    # --------------------------------------------------------
    # Convert update payload
    # --------------------------------------------------------

    update_data = payload.model_dump(exclude_unset=True)

    # --------------------------------------------------------
    # Handle destination change
    # --------------------------------------------------------

    if "destination_id" in update_data:

        destination = _get_destination(
            db,
            update_data["destination_id"],
        )

        # Update FK
        update_data["destination_id"] = destination.id

        # Keep legacy text field synchronized
        update_data["destination"] = destination.place_name

    elif "destination" in update_data:
        """
        Do not allow the old text field to change
        independently of destination_id.

        Since destination_id is now authoritative,
        ignore a standalone destination text update.
        """

        update_data.pop("destination", None)

    # --------------------------------------------------------
    # Update itinerary
    # --------------------------------------------------------

    if "itinerary" in update_data and update_data["itinerary"] is not None:
        update_data["itinerary"] = [
            item if isinstance(item, dict) else item.model_dump()
            for item in update_data["itinerary"]
        ]

    # --------------------------------------------------------
    # Update images
    # --------------------------------------------------------

    if "images" in update_data and update_data["images"] is not None:
        update_data["images"] = [
            img if isinstance(img, dict) else img.model_dump()
            for img in update_data["images"]
        ]

    # --------------------------------------------------------
    # Generate new slug when title changes
    # --------------------------------------------------------

    if "title" in update_data and update_data["title"] != pkg.title:
        update_data["slug"] = unique_slug(
            db,
            Package,
            update_data["title"],
            exclude_id=pkg.id,
        )

    # --------------------------------------------------------
    # Display order: take it out of update_data,
    # it is applied by _place_in_order below
    # --------------------------------------------------------

    has_order_change = "display_order" in update_data
    new_order = update_data.pop("display_order", None)

    # --------------------------------------------------------
    # Apply updates
    # --------------------------------------------------------

    for field, value in update_data.items():
        setattr(
            pkg,
            field,
            value,
        )

    # --------------------------------------------------------
    # Display order: reposition and renumber everything 1..n
    # --------------------------------------------------------

    if has_order_change and new_order is not None:
        _place_in_order(
            db,
            pkg,
            new_order,
            exclude_id=pkg.id,
        )

    # --------------------------------------------------------
    # Save (reorder + update in one transaction)
    # --------------------------------------------------------

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(pkg)

    # --------------------------------------------------------
    # Clear related caches
    # --------------------------------------------------------

    _invalidate_all_related_cache()

    return pkg


# ============================================================
# DELETE PACKAGE
# ============================================================


def delete_package(
    db: Session,
    package_id: int,
) -> None:
    """
    Delete a package and renumber the remaining ones 1..n.
    """

    pkg = db.query(Package).filter(Package.id == package_id).first()

    if not pkg:
        raise HTTPException(
            status_code=404,
            detail="Package not found",
        )

    db.delete(pkg)
    db.flush()

    _normalize_display_orders(db)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    # --------------------------------------------------------
    # Clear related caches
    # --------------------------------------------------------

    _invalidate_all_related_cache()


# ============================================================
# ONE-TIME UTILITY — RENUMBER display_order AS 1, 2, 3, ...
# ============================================================


def renumber_display_orders(db: Session) -> int:
    """
    Optional: run once to clean existing data immediately.
    (Every create / update / delete now also keeps orders clean.)

    Returns the number of packages renumbered.
    """

    _normalize_display_orders(db)

    db.commit()

    _invalidate_all_related_cache()

    return db.query(Package).count()


































# from typing import Optional

# from sqlalchemy.orm import Session
# from fastapi import HTTPException

# from app.models.package import Package, StatusEnum
# from app.models.most_visited import MostVisited

# from app.schemas.package import (
#     PackageCreate,
#     PackageUpdate,
# )

# from app.core.redis_client import (
#     cache_get,
#     cache_set,
#     cache_delete_pattern,
# )

# from app.core.slugify import unique_slug

# CACHE_PREFIX = "packages"


# # ============================================================
# # SERIALIZATION
# # ============================================================


# def _serialize(pkg: Package) -> dict:
#     """
#     Convert a Package SQLAlchemy object into a JSON-safe dictionary.
#     """

#     return {
#         "id": pkg.id,
#         "title": pkg.title,
#         "slug": pkg.slug,
#         # Existing display/compatibility field
#         "destination": pkg.destination,
#         # NEW: actual destination relationship
#         "destination_id": pkg.destination_id,
#         # ----------------------------------------------------
#         # Package classification
#         # ----------------------------------------------------
#         "package_type": (pkg.package_type.value if pkg.package_type else None),
#         # ----------------------------------------------------
#         # Admin-controlled display order
#         # ----------------------------------------------------
#         "display_order": pkg.display_order,
#         # ----------------------------------------------------
#         # Discovery / visibility flags
#         # ----------------------------------------------------
#         "is_popular": bool(pkg.is_popular),
#         "is_recommended": bool(pkg.is_recommended),
#         "is_trending": bool(pkg.is_trending),
#         "is_featured": bool(pkg.is_featured),
#         "is_new": bool(pkg.is_new),
#         "is_most_visited": bool(pkg.is_most_visited),
#         # ----------------------------------------------------
#         # Pricing & duration
#         # ----------------------------------------------------
#         "price": str(pkg.price),
#         "duration_days": pkg.duration_days,
#         "duration_nights": pkg.duration_nights,
#         # ----------------------------------------------------
#         # Description
#         # ----------------------------------------------------
#         "description": pkg.description,
#         # ----------------------------------------------------
#         # Images & itinerary
#         # ----------------------------------------------------
#         "images": pkg.images or [],
#         "itinerary": pkg.itinerary or [],
#         # ----------------------------------------------------
#         # Package details
#         # ----------------------------------------------------
#         "facilities": pkg.facilities or [],
#         "inclusions": pkg.inclusions or [],
#         "exclusions": pkg.exclusions or [],
#         # ----------------------------------------------------
#         # Package policies
#         # ----------------------------------------------------
#         "terms_and_conditions": pkg.terms_and_conditions,
#         "cancellation_policy": pkg.cancellation_policy,
#         # ----------------------------------------------------
#         # Status
#         # ----------------------------------------------------
#         "status": (pkg.status.value if pkg.status else None),
#         # ----------------------------------------------------
#         # Metadata
#         # ----------------------------------------------------
#         "created_by": pkg.created_by,
#         "created_at": (pkg.created_at.isoformat() if pkg.created_at else None),
#         "updated_at": (pkg.updated_at.isoformat() if pkg.updated_at else None),
#     }


# # ============================================================
# # DESTINATION VALIDATION
# # ============================================================


# def _get_destination(
#     db: Session,
#     destination_id: int,
# ) -> MostVisited:
#     """
#     Find the destination referenced by destination_id.

#     Only published destinations can be assigned to packages.
#     """

#     destination = (
#         db.query(MostVisited)
#         .filter(
#             MostVisited.id == destination_id,
#             MostVisited.status == "published",
#         )
#         .first()
#     )

#     if not destination:
#         raise HTTPException(
#             status_code=400,
#             detail="Invalid or unpublished destination",
#         )

#     return destination


# # ============================================================
# # CACHE
# # ============================================================


# def _invalidate_cache() -> None:
#     """
#     Wipe every cached packages:* key.
#     """

#     cache_delete_pattern(f"{CACHE_PREFIX}:*")


# def _invalidate_destination_cache() -> None:
#     """
#     Packages are included inside destination responses.

#     Therefore, whenever a package changes, cached
#     MostVisited/destination responses must also be cleared.
#     """

#     cache_delete_pattern("most_visited:*")


# def _invalidate_all_related_cache() -> None:
#     """
#     Clear both package and destination caches.
#     """

#     _invalidate_cache()
#     _invalidate_destination_cache()


# # ============================================================
# # PUBLIC — GET ALL PUBLISHED PACKAGES
# # ============================================================


# def get_published_packages(
#     db: Session,
#     collection: Optional[str] = None,
# ) -> list[dict]:
#     """
#     Public endpoint.

#     Returns only published packages.

#     Optional discovery collections:

#         /packages
#         /packages?collection=popular
#         /packages?collection=recommended
#         /packages?collection=trending
#         /packages?collection=featured
#         /packages?collection=new
#         /packages?collection=most_visited
#     """

#     collection = collection.strip().lower() if collection else None

#     collection_filters = {
#         "popular": Package.is_popular,
#         "recommended": Package.is_recommended,
#         "trending": Package.is_trending,
#         "featured": Package.is_featured,
#         "new": Package.is_new,
#         "most_visited": Package.is_most_visited,
#     }

#     if collection and collection not in collection_filters:
#         raise HTTPException(
#             status_code=400,
#             detail=(
#                 "Invalid collection. "
#                 "Allowed values: "
#                 "popular, recommended, trending, "
#                 "featured, new, most_visited."
#             ),
#         )

#     if collection:
#         cache_key = f"{CACHE_PREFIX}:" f"published:" f"{collection}"
#     else:
#         cache_key = f"{CACHE_PREFIX}:published"

#     cached = cache_get(cache_key)

#     if cached is not None:
#         return cached

#     query = db.query(Package).filter(Package.status == StatusEnum.published)

#     if collection:
#         query = query.filter(collection_filters[collection].is_(True))

#     packages = query.order_by(
#         Package.display_order.asc(),
#         Package.created_at.desc(),
#     ).all()

#     data = [_serialize(package) for package in packages]

#     cache_set(cache_key, data)

#     return data


# # ============================================================
# # PUBLIC / ADMIN — GET PACKAGE BY ID
# # ============================================================


# def get_package_by_id(
#     db: Session,
#     package_id: int,
# ) -> dict:
#     """
#     Get a package by ID.

#     This function does not restrict status, so it can return
#     both draft and published packages.

#     Public routes should preferably use get_package_by_slug().
#     """

#     cache_key = f"{CACHE_PREFIX}:id:{package_id}"

#     cached = cache_get(cache_key)

#     if cached is not None:
#         return cached

#     pkg = db.query(Package).filter(Package.id == package_id).first()

#     if not pkg:
#         raise HTTPException(
#             status_code=404,
#             detail="Package not found",
#         )

#     data = _serialize(pkg)

#     cache_set(cache_key, data)

#     return data


# # ============================================================
# # PUBLIC — GET PACKAGE BY SLUG
# # ============================================================


# def get_package_by_slug(
#     db: Session,
#     slug: str,
# ) -> dict:
#     """
#     Get a published package by slug.
#     Used by the public package detail page.
#     """

#     cache_key = f"{CACHE_PREFIX}:slug:{slug}"

#     cached = cache_get(cache_key)

#     if cached is not None:
#         return cached

#     pkg = (
#         db.query(Package)
#         .filter(
#             Package.slug == slug,
#             Package.status == StatusEnum.published,
#         )
#         .first()
#     )

#     if not pkg:
#         raise HTTPException(
#             status_code=404,
#             detail="Package not found",
#         )

#     data = _serialize(pkg)

#     cache_set(cache_key, data)

#     return data


# # ============================================================
# # ADMIN — GET ALL PACKAGES
# # ============================================================


# def get_all_packages_admin(
#     db: Session,
# ) -> list[dict]:
#     """
#     Admin/creator view.

#     Includes:
#     - draft packages
#     - published packages
#     """

#     packages = (
#         db.query(Package)
#         .order_by(
#             Package.display_order.asc(),
#             Package.created_at.desc(),
#         )
#         .all()
#     )

#     return [_serialize(package) for package in packages]


# # ============================================================
# # CREATE PACKAGE
# # ============================================================


# def create_package(
#     db: Session,
#     payload: PackageCreate,
#     user_id: int,
# ) -> Package:
#     """
#     Create a new package.

#     destination_id is the authoritative destination relationship.
#     The legacy destination text field is synchronized automatically.
#     """

#     # --------------------------------------------------------
#     # Validate destination
#     # --------------------------------------------------------

#     destination = _get_destination(
#         db,
#         payload.destination_id,
#     )

#     # --------------------------------------------------------
#     # Generate unique slug
#     # --------------------------------------------------------

#     slug = unique_slug(
#         db,
#         Package,
#         payload.title,
#     )

#     # --------------------------------------------------------
#     # Convert payload
#     # --------------------------------------------------------

#     package_data = payload.model_dump(
#         exclude={
#             "images",
#             "itinerary",
#             "destination",
#         }
#     )

#     # --------------------------------------------------------
#     # Create package
#     # --------------------------------------------------------

#     # destination_id is authoritative from the resolved destination
#     package_data.pop("destination_id", None)

#     pkg = Package(
#         **package_data,
#         # destination_id is authoritative
#         destination_id=destination.id,
#         # Keep old destination column synchronized
#         destination=destination.place_name,
#         # Convert Pydantic image objects
#         images=[img.model_dump() for img in payload.images],
#         # Convert itinerary objects
#         itinerary=[item.model_dump() for item in payload.itinerary],
#         slug=slug,
#         created_by=user_id,
#     )

#     # --------------------------------------------------------
#     # Save
#     # --------------------------------------------------------

#     db.add(pkg)

#     try:
#         db.commit()
#     except Exception:
#         db.rollback()
#         raise

#     db.refresh(pkg)

#     # --------------------------------------------------------
#     # Clear related caches
#     # --------------------------------------------------------

#     _invalidate_all_related_cache()

#     return pkg


# # ============================================================
# # UPDATE PACKAGE
# # ============================================================


# def update_package(
#     db: Session,
#     package_id: int,
#     payload: PackageUpdate,
# ) -> Package:
#     """
#     Update an existing package.

#     destination_id is the authoritative destination relationship.
#     """

#     # --------------------------------------------------------
#     # Find package
#     # --------------------------------------------------------

#     pkg = db.query(Package).filter(Package.id == package_id).first()

#     if not pkg:
#         raise HTTPException(
#             status_code=404,
#             detail="Package not found",
#         )

#     # --------------------------------------------------------
#     # Convert update payload
#     # --------------------------------------------------------

#     update_data = payload.model_dump(exclude_unset=True)

#     # --------------------------------------------------------
#     # Handle destination change
#     # --------------------------------------------------------

#     if "destination_id" in update_data:

#         destination = _get_destination(
#             db,
#             update_data["destination_id"],
#         )

#         # Update FK
#         update_data["destination_id"] = destination.id

#         # Keep legacy text field synchronized
#         update_data["destination"] = destination.place_name

#     elif "destination" in update_data:
#         """
#         Do not allow the old text field to change
#         independently of destination_id.

#         Since destination_id is now authoritative,
#         ignore a standalone destination text update.
#         """

#         update_data.pop("destination", None)

#     # --------------------------------------------------------
#     # Update itinerary
#     # --------------------------------------------------------

#     if "itinerary" in update_data and update_data["itinerary"] is not None:
#         update_data["itinerary"] = [
#             item if isinstance(item, dict) else item.model_dump()
#             for item in update_data["itinerary"]
#         ]

#     # --------------------------------------------------------
#     # Update images
#     # --------------------------------------------------------

#     if "images" in update_data and update_data["images"] is not None:
#         update_data["images"] = [
#             img if isinstance(img, dict) else img.model_dump()
#             for img in update_data["images"]
#         ]

#     # --------------------------------------------------------
#     # Generate new slug when title changes
#     # --------------------------------------------------------

#     if "title" in update_data and update_data["title"] != pkg.title:
#         update_data["slug"] = unique_slug(
#             db,
#             Package,
#             update_data["title"],
#             exclude_id=pkg.id,
#         )

#     # --------------------------------------------------------
#     # Apply updates
#     # --------------------------------------------------------

#     for field, value in update_data.items():
#         setattr(
#             pkg,
#             field,
#             value,
#         )

#     # --------------------------------------------------------
#     # Save
#     # --------------------------------------------------------

#     db.commit()
#     db.refresh(pkg)

#     # --------------------------------------------------------
#     # Clear related caches
#     # --------------------------------------------------------

#     _invalidate_all_related_cache()

#     return pkg


# # ============================================================
# # DELETE PACKAGE
# # ============================================================


# def delete_package(
#     db: Session,
#     package_id: int,
# ) -> None:
#     """
#     Delete a package.
#     """

#     pkg = db.query(Package).filter(Package.id == package_id).first()

#     if not pkg:
#         raise HTTPException(
#             status_code=404,
#             detail="Package not found",
#         )

#     db.delete(pkg)

#     db.commit()

#     # --------------------------------------------------------
#     # Clear related caches
#     # --------------------------------------------------------

#     _invalidate_all_related_cache()
