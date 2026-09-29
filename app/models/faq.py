from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.database import Base


class FAQ(Base):
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, index=True)

    question = Column(String(300), nullable=False)

    answer = Column(Text, nullable=False)

    category = Column(
        String(50),
        nullable=False,
        default="general",
        server_default="general",
        index=True,
    )

    # Position INSIDE its category (1, 2, 3, ...). Lower numbers appear first.
    # Kept unique and sequential per category by faq_service._place_in_order.
    display_order = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        index=True,
    )

    # published / draft
    status = Column(
        String(20),
        nullable=False,
        default="published",
        server_default="published",
        index=True,
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )