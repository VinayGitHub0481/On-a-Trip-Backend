from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.package_batch import (
    PackageBatchCreate,
    PackageBatchUpdate,
    PackageBatchOut,
)
from app.services import package_batch_service
from app.core.deps import require_admin_or_creator

router = APIRouter(
    prefix="/package-batches",
    tags=["Package Batches"],
)


# ============================================================
# PUBLIC ROUTES
# ============================================================


@router.get(
    "/upcoming",
    response_model=list[dict],
)
def list_upcoming_batches(
    db: Session = Depends(get_db),
):
    """
    Get all upcoming published package batches.

    Only returns:
    - published batches
    - batches whose departure date is today or later
    - batches belonging to published packages
    """
    return package_batch_service.get_upcoming_batches(
        db,
    )


@router.get(
    "/slug/{slug}",
    response_model=dict,
)
def get_batch_by_slug(
    slug: str,
    db: Session = Depends(get_db),
):
    """
    Get a published package batch by slug.

    Used by the public batch details page.

    Example:
    /package-batches/slug/kerala-backwaters-hills-2026-10-10
    """
    return package_batch_service.get_package_batch_by_slug(
        db,
        slug,
    )


@router.get(
    "/package/{package_id}",
    response_model=list[dict],
)
def list_package_batches(
    package_id: int,
    db: Session = Depends(get_db),
):
    """
    Get upcoming published batches
    for a specific package.
    """
    return package_batch_service.get_package_batches(
        db,
        package_id,
    )


# ============================================================
# ADMIN / CREATOR ROUTES
# ============================================================


@router.get(
    "/admin/all",
    response_model=list[dict],
    dependencies=[Depends(require_admin_or_creator)],
)
def list_all_batches(
    db: Session = Depends(get_db),
):
    """
    Get all package batches for
    admin/creator management.

    Includes:
    - draft batches
    - published batches
    - expired batches
    """
    return package_batch_service.get_all_batches_admin(
        db,
    )


@router.get(
    "/admin/{batch_id}",
    response_model=dict,
    dependencies=[Depends(require_admin_or_creator)],
)
def get_batch(
    batch_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a package batch by ID
    for admin/creator management.
    """
    return package_batch_service.get_package_batch_by_id(
        db,
        batch_id,
    )


@router.post(
    "/admin",
    response_model=PackageBatchOut,
    dependencies=[Depends(require_admin_or_creator)],
)
def create_batch(
    payload: PackageBatchCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new package batch.
    """
    return package_batch_service.create_package_batch(
        db,
        payload,
    )


@router.put(
    "/admin/{batch_id}",
    response_model=PackageBatchOut,
    dependencies=[Depends(require_admin_or_creator)],
)
def update_batch(
    batch_id: int,
    payload: PackageBatchUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing package batch.
    """
    return package_batch_service.update_package_batch(
        db,
        batch_id,
        payload,
    )


@router.delete(
    "/admin/{batch_id}",
    status_code=204,
    dependencies=[Depends(require_admin_or_creator)],
)
def delete_batch(
    batch_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete a package batch.
    """
    package_batch_service.delete_package_batch(
        db,
        batch_id,
    )
