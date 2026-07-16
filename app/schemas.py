from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=255)
    title: str = Field(default="New Chat", max_length=500)


class SessionUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=500)
    is_favorite: bool | None = None


class SessionResponse(BaseModel):
    id: UUID
    user_id: str
    title: str
    is_favorite: bool
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    sender: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1)
    context: str | None = None


class MessageResponse(BaseModel):
    id: UUID
    session_id: UUID
    sender: str
    content: str
    context: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedMessages(BaseModel):
    items: list[MessageResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class HealthResponse(BaseModel):
    status: str
    database: str
