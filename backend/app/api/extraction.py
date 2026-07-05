"""
Extraction API.

Endpoints
---------
POST    /documents/{document_id}/extract
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
from app.schemas.extraction import ExtractionResponse
from app.services.document_service import DocumentService
from app.services.extraction_service import ExtractionService
from db.postgres import get_db

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

_document_service = DocumentService()
_extraction_service = ExtractionService()


@router.post("/{document_id}/extract", response_model=ExtractionResponse)
@limiter.limit("10/minute")
async def extract_document(
    document_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Auto-detect document type and extract key structured fields."""

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
    result = await loop.run_in_executor(
        request.app.state.executor,
        functools.partial(_extraction_service.extract, document.extracted_text),
    )
    return ExtractionResponse(**result)
