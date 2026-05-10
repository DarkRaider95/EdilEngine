"""RAG service for chatbot with retrieval-augmented generation."""

import json
import logging
from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from uuid import UUID, uuid4

from openai import AsyncOpenAI
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import ServerSentEvent

from app.config import get_settings
from app.models.chat import ChatMessage, ChatSession
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

settings = get_settings()

SYSTEM_PROMPT = """Sei un assistente esperto di diritto edilizio italiano.
Rispondi SOLO basandoti sui documenti normativi forniti.
Cita sempre gli articoli e le leggi a cui fai riferimento.
Se la risposta non è nei documenti, dillo onestamente.
Le risposte devono essere in italiano, chiare e per un pubblico non tecnico.
Quando possibile, dai indicazioni pratiche e passo-passo."""


class RAGService:
    """RAG pipeline: retrieve relevant chunks → generate response → cite sources."""

    def __init__(self, db_session: AsyncSession) -> None:
        self.db = db_session
        self.openai_client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )
        self.embedding_service = EmbeddingService()

    async def _retrieve_chunks(
        self, query: str, top_k: int = 5
    ) -> list[dict]:
        """Retrieve top-K most similar chunks using pgvector.

        Args:
            query: User query text.
            top_k: Number of chunks to retrieve.

        Returns:
            List of dicts with chunk_text, legge_id, similarity, etc.
        """
        query_embedding = await self.embedding_service.generate_embedding(query)

        search_sql = text("""
            SELECT
                ec.id AS chunk_id,
                ec.legge_id,
                ec.chunk_text,
                ec.chunk_index,
                1 - (ec.embedding <=> :embedding) AS similarity,
                l.titolo AS legge_titolo,
                l.tipo AS legge_tipo,
                l.numero AS legge_numero,
                l.url_fonte AS legge_url_fonte
            FROM embedding_chunks ec
            JOIN leggi l ON l.id = ec.legge_id
            ORDER BY ec.embedding <=> :embedding
            LIMIT :limit
        """)

        result = await self.db.execute(
            search_sql,
            {"embedding": str(query_embedding), "limit": top_k},
        )
        rows = result.mappings().all()

        chunks = []
        for row in rows:
            chunks.append({
                "chunk_id": str(row["chunk_id"]),
                "legge_id": str(row["legge_id"]),
                "chunk_text": row["chunk_text"],
                "chunk_index": row["chunk_index"],
                "similarity": float(row["similarity"]),
                "legge_titolo": row["legge_titolo"],
                "legge_tipo": row["legge_tipo"],
                "legge_numero": row["legge_numero"],
                "legge_url_fonte": row["legge_url_fonte"],
            })

        return chunks

    async def _get_chat_history(
        self, session_id: str, max_messages: int = 10
    ) -> list[dict]:
        """Retrieve recent chat history for context.

        Args:
            session_id: The chat session identifier.
            max_messages: Maximum number of messages to retrieve.

        Returns:
            List of message dicts with role and content.
        """
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(max_messages)
        )
        result = await self.db.execute(stmt)
        messages = result.scalars().all()

        # Reverse to get chronological order
        return [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(messages)
            if msg.content
        ]

    async def _build_prompt(
        self,
        chunks: list[dict],
        chat_history: list[dict],
        user_query: str,
    ) -> list[dict]:
        """Build the messages list for the OpenAI chat completion.

        Args:
            chunks: Retrieved context chunks.
            chat_history: Recent conversation history.
            user_query: Current user query.

        Returns:
            List of message dicts for OpenAI API.
        """
        # Build context from chunks
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            legge_ref = chunk.get("legge_titolo", "N/A")
            legge_numero = chunk.get("legge_numero", "")
            ref = f"{legge_ref}"
            if legge_numero:
                ref += f" ({legge_numero})"
            context_parts.append(
                f"[Documento {i}] {ref}:\n{chunk['chunk_text']}"
            )

        context = "\n\n".join(context_parts) if context_parts else "Nessun documento pertinente trovato."

        messages: list[dict] = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]

        # Add chat history
        for msg in chat_history:
            messages.append(msg)

        # Add current query with context
        user_message = (
            f"Contesto normativo:\n{context}\n\n"
            f"Domanda dell'utente: {user_query}"
        )
        messages.append({"role": "user", "content": user_message})

        return messages

    async def chat(
        self,
        session_id: str,
        user_message: str,
        top_k: int = 5,
    ) -> AsyncGenerator[str, None]:
        """Process a chat message through the RAG pipeline with SSE streaming.

        Pipeline:
        1. Save user message to DB
        2. Generate embedding and retrieve relevant chunks
        3. Build prompt with context + history + query
        4. Stream GPT-4o response via SSE
        5. Save assistant response with sources to DB

        Args:
            session_id: The chat session identifier.
            user_message: The user's message content.
            top_k: Number of chunks to retrieve.

        Yields:
            SSE-formatted strings (chunks of the response).
        """
        # Step 1: Save user message
        user_msg = ChatMessage(
            id=uuid4(),
            session_id=session_id,
            role="user",
            content=user_message,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(user_msg)
        await self.db.flush()

        # Step 2: Retrieve relevant chunks
        chunks = await self._retrieve_chunks(user_message, top_k=top_k)

        # Send retrieval info as SSE event
        yield f"data: {json.dumps({'type': 'retrieval', 'retrieved_count': len(chunks)})}\n\n"

        # Step 3: Get chat history and build prompt
        chat_history = await self._get_chat_history(session_id, max_messages=10)
        messages = await self._build_prompt(chunks, chat_history, user_message)

        # Step 4: Stream GPT-4o response
        full_response = ""
        sources = []

        try:
            stream = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_CHAT_MODEL,
                messages=messages,
                stream=True,
                temperature=0.3,
                max_tokens=2048,
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    # Yield content as SSE event
                    yield f"data: {json.dumps({'type': 'message', 'content': content})}\n\n"

        except Exception as e:
            logger.error(f"Error during OpenAI streaming: {e}")
            error_msg = "Si è verificato un errore durante la generazione della risposta."
            yield f"data: {json.dumps({'type': 'error', 'detail': error_msg})}\n\n"
            full_response = error_msg

        # Step 5: Build sources from retrieved chunks
        for chunk in chunks:
            sources.append({
                "legge_id": chunk["legge_id"],
                "legge_titolo": chunk["legge_titolo"],
                "legge_numero": chunk.get("legge_numero"),
                "legge_url_fonte": chunk.get("legge_url_fonte"),
                "similarity": chunk["similarity"],
            })

        # Save assistant response
        assistant_msg = ChatMessage(
            id=uuid4(),
            session_id=session_id,
            role="assistant",
            content=full_response,
            sources=sources,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(assistant_msg)
        await self.db.commit()

        # Send done event
        yield f"data: {json.dumps({'type': 'done', 'sources': sources})}\n\n"
