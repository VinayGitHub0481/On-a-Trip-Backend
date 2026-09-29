
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    JSON,
    func,
)

from app.db.database import Base


class HappyMoment(Base):
    __tablename__ = "happy_moments"

    id = Column(Integer, primary_key=True, index=True)

    slug = Column(
        String(250),
        unique=True,
        nullable=False,
        index=True,
    )

    # Cover image
    # {
    #     "url": "...",
    #     "public_id": "..."
    # }
    image = Column(JSON, nullable=False)

    # Additional images for the detailed page
    # [
    #     {
    #         "url": "...",
    #         "public_id": "..."
    #     }
    # ]
    gallery_images = Column(JSON, nullable=True)

    # Main title
    # Example: "A Perfect Goa Escape"
    title = Column(String(200), nullable=True)

    # Short caption shown on homepage
    short_caption = Column(String(300), nullable=True)

    # Destination
    # Example: "Goa"
    place_name = Column(String(150), nullable=True)

    # Information about the destination
    place_description = Column(String(1000), nullable=True)

    # Full traveller experience
    experience = Column(String(2000), nullable=True)

    # Things travellers liked
    # [
    #     "Beautiful beaches",
    #     "Amazing sunsets",
    #     "Great food"
    # ]
    highlights = Column(JSON, nullable=True)

    # Optional trip date
    travel_date = Column(Date, nullable=True)

    # Homepage ordering (1, 2, 3, ...).
    # Kept unique and sequential by happy_moment_service._place_in_order.
    display_order = Column(Integer, default=0, nullable=False, index=True)

    # Show this moment on homepage
    is_featured = Column(Boolean, default=False, nullable=False)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    updated_at = Column(DateTime(timezone=True), onupdate=func.now())