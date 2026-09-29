from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.happy_moment import (
    HappyMomentCreate,
    HappyMomentUpdate,
    HappyMomentOut,
)
from app.services import happy_moment_service
from app.core.deps import require_admin_or_creator
from app.models.user import User

router = APIRouter(
    prefix="/happy-moments",
    tags=["Happy Moments"],
)


# ============================================================
# GET ALL HAPPY MOMENTS
# ============================================================


@router.get(
    "",
    response_model=list[dict],
)
def list_happy_moments(
    db: Session = Depends(get_db),
):
    return happy_moment_service.get_all(db)


# ============================================================
# GET FEATURED HAPPY MOMENTS
# ============================================================


@router.get(
    "/featured",
    response_model=list[dict],
)
def list_featured_happy_moments(
    limit: int = 6,
    db: Session = Depends(get_db),
):
    return happy_moment_service.get_featured(
        db,
        limit=limit,
    )


# ============================================================
# CREATE HAPPY MOMENT - ADMIN
# ============================================================


@router.post(
    "/admin",
    response_model=HappyMomentOut,
)
def create(
    payload: HappyMomentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_creator),
):
    return happy_moment_service.create(
        db,
        payload,
        current_user.id,
    )


# ============================================================
# UPDATE HAPPY MOMENT - ADMIN
# ============================================================


@router.put(
    "/admin/{item_id}",
    response_model=HappyMomentOut,
    dependencies=[Depends(require_admin_or_creator)],
)
def update(
    item_id: int,
    payload: HappyMomentUpdate,
    db: Session = Depends(get_db),
):
    return happy_moment_service.update(
        db,
        item_id,
        payload,
    )


# ============================================================
# DELETE HAPPY MOMENT - ADMIN
# ============================================================


@router.delete(
    "/admin/{item_id}",
    status_code=204,
    dependencies=[Depends(require_admin_or_creator)],
)
def delete(
    item_id: int,
    db: Session = Depends(get_db),
):
    happy_moment_service.delete(
        db,
        item_id,
    )

    return None


# ============================================================
# GET SINGLE HAPPY MOMENT BY SLUG
# ============================================================
# IMPORTANT:
# Keep this route AFTER /featured and /admin routes.
#
# Example:
# GET /happy-moments/perfect-goa-escape
# ============================================================


@router.get(
    "/{slug}",
    response_model=dict,
)
def get_happy_moment(
    slug: str,
    db: Session = Depends(get_db),
):
    return happy_moment_service.get_by_slug(
        db,
        slug,
    )
