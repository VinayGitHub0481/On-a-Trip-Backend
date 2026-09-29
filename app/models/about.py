from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    JSON,
    String,
    Text,
)

from app.db.database import Base

# ============================================================
# ABOUT PAGE
# ============================================================


class AboutPage(Base):
    __tablename__ = "about_page"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    company_name = Column(
        String(200),
        nullable=False,
    )

    hero_title = Column(
        String(250),
        nullable=False,
    )

    hero_description = Column(
        Text,
        nullable=True,
    )

    story_title = Column(
        String(250),
        nullable=True,
    )

    story_content = Column(
        Text,
        nullable=True,
    )

    mission = Column(
        Text,
        nullable=True,
    )

    vision = Column(
        Text,
        nullable=True,
    )

    founded_year = Column(
        Integer,
        nullable=True,
    )

    years_experience = Column(
        Integer,
        nullable=True,
    )

    # Controls whether this About page is visible publicly.
    status = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


# ============================================================
# LEADERSHIP / CEO / FOUNDER
# ============================================================


class AboutLeadership(Base):
    __tablename__ = "about_leadership"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String(150),
        nullable=False,
    )

    # Automatically generated from name.
    slug = Column(
        String(180),
        unique=True,
        nullable=False,
        index=True,
    )

    designation = Column(
        String(150),
        nullable=False,
    )

    short_bio = Column(
        Text,
        nullable=True,
    )

    full_bio = Column(
        Text,
        nullable=True,
    )

    # Cloudinary object:
    # {
    #     "url": "...",
    #     "public_id": "..."
    # }
    image = Column(
        JSON,
        nullable=True,
    )

    email = Column(
        String(150),
        nullable=True,
    )

    phone = Column(
        String(30),
        nullable=True,
    )

    whatsapp = Column(
        String(30),
        nullable=True,
    )

    experience_years = Column(
        Integer,
        nullable=True,
    )

    linkedin = Column(
        String(500),
        nullable=True,
    )

    instagram = Column(
        String(500),
        nullable=True,
    )

    facebook = Column(
        String(500),
        nullable=True,
    )

    company_message = Column(
        Text,
        nullable=True,
    )

    display_order = Column(
        Integer,
        default=0,
        nullable=False,
    )

    # If false, CEO/founder is hidden from public About page.
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


# ============================================================
# TEAM MEMBERS / EMPLOYEES
# ============================================================


class AboutTeamMember(Base):
    __tablename__ = "about_team_members"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String(150),
        nullable=False,
    )

    # Automatically generated from name.
    slug = Column(
        String(180),
        unique=True,
        nullable=False,
        index=True,
    )

    designation = Column(
        String(150),
        nullable=False,
    )

    department = Column(
        String(150),
        nullable=True,
    )

    short_description = Column(
        Text,
        nullable=True,
    )

    full_description = Column(
        Text,
        nullable=True,
    )

    # Optional Cloudinary image object.
    image = Column(
        JSON,
        nullable=True,
    )

    email = Column(
        String(150),
        nullable=True,
    )

    phone = Column(
        String(30),
        nullable=True,
    )

    whatsapp = Column(
        String(30),
        nullable=True,
    )

    experience_years = Column(
        Integer,
        nullable=True,
    )

    linkedin = Column(
        String(500),
        nullable=True,
    )

    instagram = Column(
        String(500),
        nullable=True,
    )

    display_order = Column(
        Integer,
        default=0,
        nullable=False,
    )

    # Controls whether employee appears on public About page.
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    # Controls whether clicking employee opens detail page.
    show_public_profile = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


# ============================================================
# COMPANY MILESTONES
# ============================================================


class AboutMilestone(Base):
    __tablename__ = "about_milestones"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    year = Column(
        Integer,
        nullable=False,
    )

    title = Column(
        String(250),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    image = Column(
        JSON,
        nullable=True,
    )

    display_order = Column(
        Integer,
        default=0,
        nullable=False,
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


# ============================================================
# COMPANY VALUES
# ============================================================


class AboutValue(Base):
    __tablename__ = "about_values"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    title = Column(
        String(200),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    # Example: "Heart", "ShieldCheck", "MapPin"
    icon = Column(
        String(100),
        nullable=True,
    )

    display_order = Column(
        Integer,
        default=0,
        nullable=False,
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
