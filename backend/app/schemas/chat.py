"""Pydantic schemas for chat endpoints."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ChatSessionCreate(BaseModel):
    """Request to create a new chat session."""

    user_agent: str | None = Field(default=None, description="User agent string")


class ChatSessionResponse(BaseModel):
    """Response for a created chat session."""

    id: UUID
    session_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatMessageCreate(BaseModel):
    """Request to send a chat message."""

    session_id: str = Field(..., min_length=1, description="Chat session ID")
    content: str = Field(..., min_length=1, description="Message content")


class ChatMessageResponse(BaseModel):
    """Response for a single chat message."""

    id: UUID
    role: str
    content: str | None = None
    sources: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatHistoryResponse(BaseModel):
    """Response for chat session history."""

    session_id: str
    messages: list[ChatMessageResponse]
