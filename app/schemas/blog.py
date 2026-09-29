from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class BlogStatus(str, Enum):
    draft = "draft"
    published = "published"


class ImageObject(BaseModel):
    url: str
    public_id: Optional[str] = None


class BlogCreate(BaseModel):
    title: str = Field(min_length=3, max_length=220)

    excerpt: Optional[str] = Field(default=None, max_length=400)

    content: str = Field(min_length=10)

    cover_image: Optional[ImageObject] = None

    target_keyword: Optional[str] = Field(default=None, max_length=150)

    meta_description: Optional[str] = Field(default=None, max_length=300)

    status: BlogStatus = BlogStatus.draft


class BlogUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=220)

    excerpt: Optional[str] = Field(default=None, max_length=400)

    content: Optional[str] = Field(default=None, min_length=10)

    cover_image: Optional[ImageObject] = None

    target_keyword: Optional[str] = Field(default=None, max_length=150)

    meta_description: Optional[str] = Field(default=None, max_length=300)

    status: Optional[BlogStatus] = None


class BlogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    excerpt: Optional[str]
    content: str
    cover_image: Optional[dict]
    target_keyword: Optional[str]
    meta_description: Optional[str]
    status: BlogStatus
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
