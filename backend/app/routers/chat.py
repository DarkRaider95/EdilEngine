"""Router for chat endpoints with SSE streaming."""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.chat import ChatMessage, ChatSession
from app.schemas.chat import (
    ChatHistoryResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatSessionCreate,
    ChatSessionResponse,
)
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/session", response_model=ChatSessionResponse)
async def create_session(
    data: ChatSessionCreate,
    db: AsyncSession = Depends(get_db),
) -> ChatSessionResponse:
    """Create a new chat session.

    Generates a unique session_id and stores it in the database.
    """
    session_id = str(uuid.uuid4())

    session = ChatSession(
        session_id=session_id,
        user_agent=data.user_agent,
    )
    db.add(session)
    await db.flush()
    await db.refresh(session)

    return ChatSessionResponse.model_validate(session)


@router.post("/message")
async def send_message(
    data: ChatMessageCreate,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Send a message to the chatbot and receive a streaming SSE response.

    The response is streamed as Server-Sent Events with the following event types:
    - `retrieval`: Information about retrieved context chunks
    - `message`: Chunks of the generated response text
    - `done`: Final event with source citations
    - `error`: Error information if something goes wrong
    """
    # Verify session exists
    stmt = select(ChatSession).where(ChatSession.session_id == data.session_id)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Sessione chat non trovata")

    if not data.content or not data.content.strip():
        raise HTTPException(status_code=400, detail="Il messaggio non può essere vuoto")

    rag_service = RAGService(db)

    async def event_generator():
        async for event in rag_service.chat(
            session_id=data.session_id,
            user_message=data.content,
        ):
            yield event

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.get("/session/{session_id}/history", response_model=ChatHistoryResponse)
async def get_history(
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> ChatHistoryResponse:
    """Get the message history for a chat session.

    Returns all messages in chronological order.
    """
    # Verify session exists
    stmt = select(ChatSession).where(ChatSession.session_id == session_id)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Sessione chat non trovata")

    # Get messages ordered by creation time
    msg_stmt = (
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
    )
    msg_result = await db.execute(msg_stmt)
    messages = msg_result.scalars().all()

    return ChatHistoryResponse(
        session_id=session_id,
        messages=[ChatMessageResponse.model_validate(msg) for msg in messages],
    )
