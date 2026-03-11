"""Knowledge Base Schemas"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class KBCategoryCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    slug: str = Field(..., max_length=100)
    icon: Optional[str] = "BookOpen"
    color: Optional[str] = "blue"
    order: int = 0


class KBCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    order: Optional[int] = None


class KBCategoryResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    slug: str
    icon: Optional[str] = None
    color: Optional[str] = None
    order: int
    created_at: datetime
    article_count: int = 0
    model_config = ConfigDict(from_attributes=True)


class KBArticleCreate(BaseModel):
    title: str = Field(..., max_length=300)
    content: str = ""
    excerpt: Optional[str] = None
    category_id: Optional[str] = None
    tags: List[str] = []
    status: str = "draft"
    pinned: bool = False


class KBArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    category_id: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None
    pinned: Optional[bool] = None


class KBArticleResponse(BaseModel):
    id: UUID
    title: str
    slug: str
    excerpt: Optional[str] = None
    category_id: Optional[str] = None
    tags: List[str] = []
    status: str
    author_id: Optional[str] = None
    view_count: int
    helpful_count: int
    not_helpful_count: int
    pinned: bool
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class KBArticleDetailResponse(KBArticleResponse):
    content: str = ""


class KBArticleListResponse(BaseModel):
    items: List[KBArticleResponse]
    total: int
    skip: int
    limit: int
