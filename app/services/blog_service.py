from datetime import datetime, timezone

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.blog import Blog, BlogStatus
from app.schemas.blog import BlogCreate, BlogUpdate

from app.core.slugify import unique_slug

from app.core.redis_client import (
    cache_get,
    cache_set,
    cache_delete_pattern,
)

CACHE_PREFIX = "blogs"


def _serialize(blog: Blog) -> dict:
    return {
        "id": blog.id,
        "title": blog.title,
        "slug": blog.slug,
        "excerpt": blog.excerpt,
        "content": blog.content,
        "cover_image": blog.cover_image,
        "target_keyword": blog.target_keyword,
        "meta_description": blog.meta_description,
        "status": blog.status.value,
        "published_at": (blog.published_at.isoformat() if blog.published_at else None),
        "created_at": (blog.created_at.isoformat() if blog.created_at else None),
        "updated_at": (blog.updated_at.isoformat() if blog.updated_at else None),
    }


def _invalidate_cache() -> None:
    cache_delete_pattern(f"{CACHE_PREFIX}:*")


def get_published_blogs(db: Session) -> list[dict]:
    cache_key = f"{CACHE_PREFIX}:published"

    cached = cache_get(cache_key)

    if cached is not None:
        return cached

    blogs = (
        db.query(Blog)
        .filter(Blog.status == BlogStatus.published)
        .order_by(Blog.published_at.desc())
        .all()
    )

    data = [_serialize(blog) for blog in blogs]

    cache_set(cache_key, data)

    return data


def get_blog_by_slug(db: Session, slug: str) -> dict:

    cache_key = f"{CACHE_PREFIX}:slug:{slug}"

    cached = cache_get(cache_key)

    if cached is not None:
        return cached

    blog = (
        db.query(Blog)
        .filter(
            Blog.slug == slug,
            Blog.status == BlogStatus.published,
        )
        .first()
    )

    if not blog:
        raise HTTPException(status_code=404, detail="Blog post not found")

    data = _serialize(blog)

    cache_set(cache_key, data)

    return data


def get_all_blogs_admin(db: Session) -> list[Blog]:

    return db.query(Blog).order_by(Blog.created_at.desc()).all()


def create_blog(db: Session, payload: BlogCreate, user_id: int) -> Blog:

    data = payload.model_dump()

    cover_image = data.pop("cover_image", None)

    slug = unique_slug(db, Blog, payload.title)

    published_at = (
        datetime.now(timezone.utc) if payload.status == BlogStatus.published else None
    )

    blog = Blog(
        **data,
        slug=slug,
        cover_image=cover_image,
        created_by=user_id,
        published_at=published_at,
    )

    db.add(blog)
    db.commit()
    db.refresh(blog)

    _invalidate_cache()

    return blog


def update_blog(db: Session, blog_id: int, payload: BlogUpdate) -> Blog:

    blog = db.query(Blog).filter(Blog.id == blog_id).first()

    if not blog:
        raise HTTPException(status_code=404, detail="Blog post not found")

    update_data = payload.model_dump(exclude_unset=True)

    # Convert ImageObject to dictionary
    if "cover_image" in update_data and update_data["cover_image"] is not None:
        update_data["cover_image"] = (
            update_data["cover_image"].model_dump()
            if hasattr(update_data["cover_image"], "model_dump")
            else update_data["cover_image"]
        )

    # Generate a new slug if title changes
    if "title" in update_data and update_data["title"] != blog.title:
        update_data["slug"] = unique_slug(
            db, Blog, update_data["title"], exclude_id=blog.id
        )

    # Track previous status
    previous_status = blog.status

    # Apply updates
    for field, value in update_data.items():
        setattr(blog, field, value)

    # Draft → Published
    if previous_status != BlogStatus.published and blog.status == BlogStatus.published:
        blog.published_at = datetime.now(timezone.utc)

    # Published → Draft
    elif previous_status == BlogStatus.published and blog.status == BlogStatus.draft:
        blog.published_at = None

    db.commit()
    db.refresh(blog)

    _invalidate_cache()

    return blog


def delete_blog(db: Session, blog_id: int) -> None:

    blog = db.query(Blog).filter(Blog.id == blog_id).first()

    if not blog:
        raise HTTPException(status_code=404, detail="Blog post not found")

    db.delete(blog)
    db.commit()

    _invalidate_cache()
