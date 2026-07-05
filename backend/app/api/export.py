"""
Export API.

Endpoints
---------
GET  /documents/{document_id}/export/pdf   — download translated (or extracted) text as PDF
POST /export/text-pdf                      — convert arbitrary text to PDF (Translator page)
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.models.user import User
from app.services.document_service import DocumentService
from app.services.export_service import generate_pdf
from db.postgres import get_db

router = APIRouter()


class TextPdfRequest(BaseModel):
    text: str
    title: str = "translation"
    label: str = "Translated Text"


@router.post("/export/text-pdf")
def export_text_pdf(
    body: TextPdfRequest,
    current_user: User = Depends(get_current_active_user),
):
    """Convert arbitrary translated text to a downloadable PDF."""
    if not body.text.strip():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="No text provided.")
    pdf_bytes = generate_pdf(text=body.text, title=body.title, content_label=body.label)
    safe_title = body.title.replace(" ", "_")[:60]
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{safe_title}.pdf"'},
    )

_document_service = DocumentService()


@router.get("/{document_id}/export/pdf")
def export_pdf(
    document_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Return the translated text (or extracted text) as a downloadable PDF."""
    try:
        document = _document_service.get_document(
            db=db,
            document_id=document_id,
            current_user=current_user,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    # Prefer translated text; fall back to extracted text
    has_translation = bool(
        document.translated_text
        and document.translated_text != document.extracted_text
    )

    text = document.translated_text if has_translation else document.extracted_text
    if not text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Document has no text to export.",
        )

    content_label = "Translated Text" if has_translation else "Extracted Text"

    pdf_bytes = generate_pdf(
        text=text,
        title=document.filename or "document",
        content_label=content_label,
    )

    # Derive a clean download filename
    base = (document.filename or "document").rsplit(".", 1)[0]
    download_name = f"{base}_translated.pdf" if has_translation else f"{base}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{download_name}"'},
    )
