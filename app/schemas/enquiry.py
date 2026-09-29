from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EnquiryCreate(BaseModel):
    # Package the user is enquiring about.
    # None for customized enquiries.
    package_id: int | None = Field(
        default=None,
        gt=0,
    )

    # Specific batch/trip the user is enquiring about (optional).
    batch_id: int | None = Field(
        default=None,
        gt=0,
    )

    # Package category/type selected in the enquiry form.
    # Use "custom" for customized package enquiries.
    package_type: str = Field(
        ...,
        min_length=2,
        max_length=50,
    )

    # Destination is used only by the Custom Enquiry form.
    # It is NOT required for the global Plan a Trip form.
    destination: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    # Customer name.
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    # Phone / WhatsApp number.
    phone: str = Field(
        ...,
        min_length=7,
        max_length=20,
    )

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        digits = "".join(ch for ch in v if ch.isdigit())

        if len(digits) < 10:
            raise ValueError("Phone number must be at least 10 digits")

        if len(digits) > 15:
            raise ValueError("Phone number must be at most 15 digits")

        return v.strip()

    # Number of travellers.
    travellers: int = Field(
        ...,
        ge=1,
    )

    # Requested travel date.
    travel_date: date = Field(
        ...,
    )

    # Additional requirements (optional).
    message: str | None = Field(
        default=None,
        max_length=5000,
    )


class EnquiryResponse(BaseModel):
    id: int

    package_id: int | None = None

    batch_id: int | None = None

    package_type: str

    # Present for custom enquiries.
    # None for normal/global enquiries.
    destination: str | None = None

    package_title: str | None = None

    name: str

    phone: str

    travellers: int

    travel_date: date

    message: str | None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
