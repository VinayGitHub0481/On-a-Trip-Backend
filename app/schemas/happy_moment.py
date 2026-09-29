

from datetime import date, datetime

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# IMAGE
# ============================================================


class HappyMomentImage(BaseModel):
    url: str = Field(
        min_length=1,
    )

    public_id: Optional[str] = None


# ============================================================
# BASE
# ============================================================


class HappyMomentBase(BaseModel):
    title: Optional[str] = Field(
        default=None,
        max_length=200,
    )

    short_caption: Optional[str] = Field(
        default=None,
        max_length=300,
    )

    place_name: Optional[str] = Field(
        default=None,
        max_length=150,
    )

    place_description: Optional[str] = Field(
        default=None,
        max_length=1000,
    )

    experience: Optional[str] = Field(
        default=None,
        max_length=2000,
    )

    highlights: Optional[List[str]] = None

    travel_date: Optional[date] = None

    display_order: int = Field(
        default=0,
        ge=0,
    )

    is_featured: bool = False


# ============================================================
# CREATE
# ============================================================


class HappyMomentCreate(HappyMomentBase):
    # Required cover image
    image: HappyMomentImage

    # Optional additional images
    gallery_images: Optional[List[HappyMomentImage]] = None


# ============================================================
# UPDATE
# ============================================================


class HappyMomentUpdate(BaseModel):
    # Optional slug update.
    # Keep this only if admin is allowed to manually edit
    # the SEO URL.
    slug: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=250,
    )

    # Cover image
    image: Optional[HappyMomentImage] = None

    # Additional gallery images
    gallery_images: Optional[List[HappyMomentImage]] = None

    title: Optional[str] = Field(
        default=None,
        max_length=200,
    )

    short_caption: Optional[str] = Field(
        default=None,
        max_length=300,
    )

    place_name: Optional[str] = Field(
        default=None,
        max_length=150,
    )

    place_description: Optional[str] = Field(
        default=None,
        max_length=1000,
    )

    experience: Optional[str] = Field(
        default=None,
        max_length=2000,
    )

    highlights: Optional[List[str]] = None

    travel_date: Optional[date] = None

    display_order: Optional[int] = Field(
        default=None,
        ge=0,
    )

    is_featured: Optional[bool] = None


# ============================================================
# RESPONSE
# ============================================================


class HappyMomentResponse(HappyMomentBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    slug: str

    # Required because DB column is nullable=False
    image: HappyMomentImage

    # DB column is nullable=True
    gallery_images: Optional[List[HappyMomentImage]] = None

    created_by: Optional[int] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


# ============================================================
# OPTIONAL ALIAS
# ============================================================

# If existing routes use HappyMomentOut,
# they can continue using that name.
HappyMomentOut = HappyMomentResponse
