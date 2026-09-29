from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# ============================================================
# POLICY TYPE
# ============================================================


class PolicyType(str, Enum):
    terms_conditions = "terms_conditions"
    booking = "booking"
    cancellation = "cancellation"


# ============================================================
# POLICY STATUS
# ============================================================


class PolicyStatus(str, Enum):
    draft = "draft"
    published = "published"


# ============================================================
# POLICY CREATE
# ============================================================


class PolicyCreate(BaseModel):
    policy_type: PolicyType

    question: str = Field(
        min_length=3,
        max_length=300,
    )

    answer: str = Field(
        min_length=10,
    )

    # 0 means "add at the end"
    display_order: int = Field(
        default=0,
        ge=0,
    )

    status: PolicyStatus = PolicyStatus.draft


# ============================================================
# POLICY UPDATE
# ============================================================


class PolicyUpdate(BaseModel):
    policy_type: Optional[PolicyType] = None

    question: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=300,
    )

    answer: Optional[str] = Field(
        default=None,
        min_length=10,
    )

    # None = don't change the current position
    # 0 = move to the end
    display_order: Optional[int] = Field(
        default=None,
        ge=0,
    )

    status: Optional[PolicyStatus] = None


# ============================================================
# POLICY OUT
# ============================================================


class PolicyOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    policy_type: PolicyType
    question: str
    answer: str
    display_order: int
    status: PolicyStatus

    published_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]