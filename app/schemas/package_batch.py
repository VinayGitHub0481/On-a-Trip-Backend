

# Save this file as: app/schemas/package_batch.py
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

# Reuse the enums from the SQLAlchemy model so the schema and the
# service always compare the same values.
from app.models.package_batch import (
    BatchStatusEnum,
    BatchDurationModeEnum,
    BatchPriceModeEnum,
    BatchItineraryModeEnum,
    BatchInclusionsModeEnum,
    BatchExclusionsModeEnum,
    BatchTermsModeEnum,
    BatchCancellationModeEnum,
)


# ============================================================
# AVAILABILITY
# ============================================================
# Manually controlled by the admin (the website uses enquiries,
# not online booking). Stored as a plain string in the DB.


class BatchAvailabilityEnum(str, Enum):
    open = "open"
    limited = "limited"
    almost_full = "almost_full"
    full = "full"
    closed = "closed"


# ============================================================
# CUSTOM ITINERARY DAY
# ============================================================


class BatchItineraryItem(BaseModel):
    day: Optional[int] = Field(default=None, ge=1)

    title: str = Field(
        min_length=2,
        max_length=200,
    )

    description: Optional[str] = None

    # Image URL (string) or None
    image: Optional[str] = None


# ============================================================
# CREATE BATCH
# ============================================================


class PackageBatchCreate(BaseModel):
    package_id: int = Field(gt=0)

    # Position inside the package. Empty / 0 = add last.
    display_order: Optional[int] = Field(
        default=None,
        ge=0,
    )

    departure_date: date
    return_date: date

    # Duration
    duration_mode: BatchDurationModeEnum = BatchDurationModeEnum.default
    days: Optional[int] = Field(default=None, gt=0)
    nights: Optional[int] = Field(default=None, ge=0)

    # Price
    price_mode: BatchPriceModeEnum = BatchPriceModeEnum.default
    price_per_person: Optional[Decimal] = Field(default=None, gt=0)

    # Itinerary
    itinerary_mode: BatchItineraryModeEnum = BatchItineraryModeEnum.default
    custom_itinerary: Optional[list[BatchItineraryItem]] = None

    # Inclusions
    inclusions_mode: BatchInclusionsModeEnum = BatchInclusionsModeEnum.default
    custom_inclusions: Optional[list[str]] = None

    # Exclusions
    exclusions_mode: BatchExclusionsModeEnum = BatchExclusionsModeEnum.default
    custom_exclusions: Optional[list[str]] = None

    # Terms & conditions
    terms_mode: BatchTermsModeEnum = BatchTermsModeEnum.default
    custom_terms_and_conditions: Optional[list[str]] = None

    # Cancellation policy
    cancellation_mode: BatchCancellationModeEnum = BatchCancellationModeEnum.default
    custom_cancellation_policy: Optional[list[str]] = None

    # Availability / status
    availability: Optional[BatchAvailabilityEnum] = BatchAvailabilityEnum.open
    status: BatchStatusEnum = BatchStatusEnum.draft


# ============================================================
# UPDATE BATCH
# ============================================================


class PackageBatchUpdate(BaseModel):
    package_id: Optional[int] = Field(default=None, gt=0)

    # Move the batch to this position inside its package.
    # Omit to keep the current position.
    display_order: Optional[int] = Field(
        default=None,
        ge=0,
    )

    departure_date: Optional[date] = None
    return_date: Optional[date] = None

    # Duration
    duration_mode: Optional[BatchDurationModeEnum] = None
    days: Optional[int] = Field(default=None, gt=0)
    nights: Optional[int] = Field(default=None, ge=0)

    # Price
    price_mode: Optional[BatchPriceModeEnum] = None
    price_per_person: Optional[Decimal] = Field(default=None, gt=0)

    # Itinerary
    itinerary_mode: Optional[BatchItineraryModeEnum] = None
    custom_itinerary: Optional[list[BatchItineraryItem]] = None

    # Inclusions
    inclusions_mode: Optional[BatchInclusionsModeEnum] = None
    custom_inclusions: Optional[list[str]] = None

    # Exclusions
    exclusions_mode: Optional[BatchExclusionsModeEnum] = None
    custom_exclusions: Optional[list[str]] = None

    # Terms & conditions
    terms_mode: Optional[BatchTermsModeEnum] = None
    custom_terms_and_conditions: Optional[list[str]] = None

    # Cancellation policy
    cancellation_mode: Optional[BatchCancellationModeEnum] = None
    custom_cancellation_policy: Optional[list[str]] = None

    # Availability / status
    availability: Optional[BatchAvailabilityEnum] = None
    status: Optional[BatchStatusEnum] = None


# ============================================================
# BATCH OUTPUT (raw database row)
# ============================================================
# Only needed if a route uses response_model=PackageBatchOut on
# a function that returns the SQLAlchemy object (create / update).


class PackageBatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    package_id: int
    slug: str
    display_order: int

    departure_date: date
    return_date: date

    duration_mode: BatchDurationModeEnum
    days: Optional[int] = None
    nights: Optional[int] = None

    price_mode: BatchPriceModeEnum
    price_per_person: Optional[Decimal] = None

    itinerary_mode: BatchItineraryModeEnum
    custom_itinerary: Optional[list[dict[str, Any]]] = None

    inclusions_mode: BatchInclusionsModeEnum
    custom_inclusions: Optional[list[str]] = None

    exclusions_mode: BatchExclusionsModeEnum
    custom_exclusions: Optional[list[str]] = None

    terms_mode: BatchTermsModeEnum
    custom_terms_and_conditions: Optional[list[str]] = None

    cancellation_mode: BatchCancellationModeEnum
    custom_cancellation_policy: Optional[list[str]] = None

    availability: Optional[str] = None
    status: BatchStatusEnum

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None



































# from datetime import datetime
# from decimal import Decimal
# from enum import Enum
# from typing import Any, Optional

# from pydantic import BaseModel, ConfigDict, Field


# # ============================================================
# # ENUMS
# # ============================================================


# class StatusEnum(str, Enum):
#     draft = "draft"
#     published = "published"


# class PackageTypeEnum(str, Enum):
#     pilgrimage = "pilgrimage"
#     mountains_adventure = "mountains_adventure"
#     romantic = "romantic"
#     international = "international"
#     beach = "beach"
#     family = "family"
#     wildlife_nature = "wildlife_nature"


# # ============================================================
# # IMAGE OBJECT
# # ============================================================


# class ImageObject(BaseModel):
#     url: str
#     public_id: Optional[str] = None


# # ============================================================
# # CREATE PACKAGE
# # ============================================================


# class PackageCreate(BaseModel):
#     title: str = Field(
#         min_length=2,
#         max_length=200,
#     )

#     destination: str = Field(
#         min_length=2,
#         max_length=150,
#     )

#     # Matches SQLAlchemy nullable=True
#     destination_id: Optional[int] = Field(
#         default=None,
#         gt=0,
#     )

#     package_type: PackageTypeEnum = PackageTypeEnum.family

#     display_order: int = Field(
#         default=0,
#         ge=0,
#     )

#     price: Decimal = Field(
#         gt=0,
#     )

#     duration_days: int = Field(
#         gt=0,
#     )

#     duration_nights: int = Field(
#         ge=0,
#     )

#     description: Optional[str] = None

#     images: Optional[list[ImageObject]] = None

#     itinerary: Optional[list[dict[str, Any]]] = None

#     facilities: list[str] = Field(
#         default_factory=list,
#     )

#     inclusions: list[str] = Field(
#         default_factory=list,
#     )

#     exclusions: list[str] = Field(
#         default_factory=list,
#     )

#     terms_and_conditions: Optional[str] = None

#     cancellation_policy: Optional[str] = None

#     status: StatusEnum = StatusEnum.draft

#     # Discovery collections
#     is_popular: bool = False
#     is_recommended: bool = False
#     is_trending: bool = False
#     is_featured: bool = False
#     is_new: bool = False
#     is_most_visited: bool = False


# # ============================================================
# # UPDATE PACKAGE
# # ============================================================


# class PackageUpdate(BaseModel):
#     title: Optional[str] = Field(
#         default=None,
#         min_length=2,
#         max_length=200,
#     )

#     destination: Optional[str] = Field(
#         default=None,
#         min_length=2,
#         max_length=150,
#     )

#     destination_id: Optional[int] = Field(
#         default=None,
#         gt=0,
#     )

#     package_type: Optional[PackageTypeEnum] = None

#     display_order: Optional[int] = Field(
#         default=None,
#         ge=0,
#     )

#     price: Optional[Decimal] = Field(
#         default=None,
#         gt=0,
#     )

#     duration_days: Optional[int] = Field(
#         default=None,
#         gt=0,
#     )

#     duration_nights: Optional[int] = Field(
#         default=None,
#         ge=0,
#     )

#     description: Optional[str] = None

#     images: Optional[list[ImageObject]] = None

#     itinerary: Optional[list[dict[str, Any]]] = None

#     facilities: Optional[list[str]] = None

#     inclusions: Optional[list[str]] = None

#     exclusions: Optional[list[str]] = None

#     terms_and_conditions: Optional[str] = None

#     cancellation_policy: Optional[str] = None

#     status: Optional[StatusEnum] = None

#     # Discovery collections
#     is_popular: Optional[bool] = None
#     is_recommended: Optional[bool] = None
#     is_trending: Optional[bool] = None
#     is_featured: Optional[bool] = None
#     is_new: Optional[bool] = None
#     is_most_visited: Optional[bool] = None


# # ============================================================
# # PACKAGE OUTPUT
# # ============================================================


# class PackageOut(BaseModel):
#     model_config = ConfigDict(
#         from_attributes=True,
#     )

#     id: int

#     title: str

#     slug: str

#     destination: str

#     destination_id: Optional[int] = None

#     package_type: PackageTypeEnum

#     display_order: int

#     price: Decimal

#     duration_days: int

#     duration_nights: int

#     description: Optional[str] = None

#     images: Optional[list[ImageObject]] = None

#     itinerary: Optional[list[dict[str, Any]]] = None

#     facilities: list[str]

#     inclusions: list[str]

#     exclusions: list[str]

#     terms_and_conditions: Optional[str] = None

#     cancellation_policy: Optional[str] = None

#     status: StatusEnum

#     created_by: Optional[int] = None

#     created_at: datetime

#     updated_at: Optional[datetime] = None

#     # Discovery collections
#     is_popular: bool
#     is_recommended: bool
#     is_trending: bool
#     is_featured: bool
#     is_new: bool
#     is_most_visited: bool