"""Persistent chat with sliding context window — uses Phi-3 via HF Space."""
from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import get_db
from models.schemas import (
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationSummary,
    MessageItem,
)
from services.llm_service import llm_generate
from utils.context_window import build_context_prompt, trim_messages_to_window

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/conversations", response_model=dict)
async def create_conversation(db: Annotated[AsyncSession, Depends(get_db)]) -> dict:
    """Create a new conversation and return its ID."""
    conv_id = str(uuid.uuid4())
    await db.execute(
        text(
            "INSERT INTO conversations (id, created_at) VALUES (:id, NOW())"
        ),
        {"id": conv_id},
    )
    await db.commit()
    return {"conversation_id": conv_id}


@router.get("/conversations", response_model=list[ConversationSummary])
async def list_conversations(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> list[ConversationSummary]:
    """Return all conversations ordered by most recent."""
    result = await db.execute(
        text(
            "SELECT id, created_at FROM conversations c ORDER BY created_at DESC LIMIT 50"
        )
    )
    rows = result.fetchall()
    return [
        ConversationSummary(
            id=row.id,
            title="",
            created_at=row.created_at,
        )
        for row in rows
    ]


@router.post("/conversations/{conversation_id}/messages", response_model=ChatMessageResponse)
async def send_message(
    conversation_id: str,
    request: ChatMessageRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ChatMessageResponse:
    """Add a user message and return the model's reply."""
    # Verify conversation exists
    result = await db.execute(
        text("SELECT id FROM conversations WHERE id = :id"),
        {"id": conversation_id},
    )
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Fetch message history as dicts (required by context_window utils)
    result = await db.execute(
        text(
            "SELECT role, content FROM messages "
            "WHERE conversation_id = :cid ORDER BY created_at ASC"
        ),
        {"cid": conversation_id},
    )
    history = [{"role": row.role, "content": row.content} for row in result.fetchall()]

    # Build context-window-trimmed prompt
    # ChatMessageRequest uses `content` field
    history.append({"role": "user", "content": request.content})
    trimmed, summary = trim_messages_to_window(history)
    prompt = build_context_prompt(trimmed, summary)

    # Generate response
    reply = await llm_generate(prompt, max_tokens=512)

    # Persist user message + assistant reply
    msg_id_user = str(uuid.uuid4())
    msg_id_asst = str(uuid.uuid4())
    await db.execute(
        text(
            "INSERT INTO messages (id, conversation_id, role, content, created_at) "
            "VALUES (:id, :cid, 'user', :content, NOW())"
        ),
        {"id": msg_id_user, "cid": conversation_id, "content": request.content},
    )
    await db.execute(
        text(
            "INSERT INTO messages (id, conversation_id, role, content, created_at) "
            "VALUES (:id, :cid, 'assistant', :content, NOW())"
        ),
        {"id": msg_id_asst, "cid": conversation_id, "content": reply},
    )
    await db.commit()

    from datetime import datetime

    return ChatMessageResponse(
        message_id=msg_id_asst,
        conversation_id=conversation_id,
        role="assistant",
        content=reply,
        created_at=datetime.utcnow(),
    )


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageItem])
async def get_messages(
    conversation_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[MessageItem]:
    """Return full message history for a conversation."""
    result = await db.execute(
        text(
            "SELECT id, role, content, created_at FROM messages "
            "WHERE conversation_id = :cid ORDER BY created_at ASC"
        ),
        {"cid": conversation_id},
    )
    return [
        MessageItem(id=row.id, role=row.role, content=row.content, created_at=row.created_at)
        for row in result.fetchall()
    ]
