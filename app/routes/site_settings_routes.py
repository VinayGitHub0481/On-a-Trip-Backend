from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.site_settings import (
    SiteSettingsUpdate,
    SiteSettingsOut,
)
from app.services import site_settings_service
from app.core.deps import require_admin

router = APIRouter(
    prefix="/settings",
    tags=["Website Settings"],
)


@router.get(
    "",
    response_model=SiteSettingsOut,
)
def get_settings(
    db: Session = Depends(get_db),
):
    """
    Public endpoint.

    The frontend reads this endpoint for:
    - Offer banner
    - Homepage headline
    - Trust line
    - Phone number
    - WhatsApp number
    - Company address
    - Google Maps URL
    - Featured destinations
    - Top Info Bar settings
    - Social links
    - Locations
    - Traveller trust text
    """

    return site_settings_service.get_settings(db)


@router.put(
    "/admin",
    response_model=SiteSettingsOut,
    dependencies=[Depends(require_admin)],
)
def update_settings(
    payload: SiteSettingsUpdate,
    db: Session = Depends(get_db),
):
    """
    Admin-only endpoint for updating website settings.

    This updates the singleton SiteSettings row.
    Only fields included in the request are changed.
    """

    return site_settings_service.update_settings(
        db,
        payload,
    )
