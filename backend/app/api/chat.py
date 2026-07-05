"""
Chat API.

Endpoints
---------
POST    /documents/{document_id}/chat
"""

import asyncio
import functools
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import get_chat_service
from app.services.document_service import DocumentService
from db.postgres import get_db

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

_document_service = DocumentService()


@router.post("/{document_id}/chat", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat_with_document(
    document_id: UUID,
    body: ChatRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Ask a question about a specific document using the extracted text."""

    try:
        document = _document_service.get_document(
            db=db,
            document_id=document_id,
            current_user=current_user,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    if not document.extracted_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Document has no extracted text. It may still be processing.",
        )

    loop = asyncio.get_event_loop()
    reply = await loop.run_in_executor(
        request.app.state.executor,
        functools.partial(
            get_chat_service().ask,
            document.extracted_text,
            body.message,
        ),
    )

    return ChatResponse(response=reply)
