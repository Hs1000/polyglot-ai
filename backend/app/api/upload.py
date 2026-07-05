"""
Document Upload API.

Endpoints
---------
POST /upload        — save file, kick off background processing, return immediately
GET  /upload/{id}   — poll document status and result
"""

from pathlib import Path
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.models.document import Document, DocumentStatus
from app.models.user import User
from app.pipeline.document_pipeline import DocumentPipeline
from app.utils.file_utils import save_upload_file
from db.postgres import SessionLocal, get_db

router = APIRouter()

pipeline = DocumentPipeline()

_ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg"}
_MAX_UPLOAD_BYTES = 20 * 1024 * 1024  # 20 MB


def _run_pipeline(document_id: UUID, file_path: Path) -> None:
    """Background task: process the document and update the DB record."""
    db: Session = SessionLocal()
    try:
        result = pipeline.process(file_path)

        doc = db.query(Document).filter(Document.id == document_id).first()
        if doc:
            doc.status = DocumentStatus.done
            doc.language = result["language"]
            doc.pages = result["pages"]
            doc.characters = result["characters"]
            doc.ocr_used = result["ocr_used"]
            doc.extracted_text = result["text"]
            doc.translated_text = result["translated_text"]
            doc.summary = result["summary"]
            db.commit()

    except Exception as exc:
        db.rollback()
        doc = db.query(Document).filter(Document.id == document_id).first()
        if doc:
            doc.status = DocumentStatus.failed
            doc.error = str(exc)
            db.commit()
    finally:
        db.close()


@router.post(
    "/",
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Save the uploaded file, create a document record, and start processing
    in the background. Returns immediately with the document ID.
    """
    # --- Type validation ---
    ext = Path(file.filename or "").suffix.lower()
    if ext not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type '{ext}' is not supported. Allowed: {', '.join(sorted(_ALLOWED_EXTENSIONS))}",
        )

    # --- Size validation (read into memory once, then reset) ---
    contents = await file.read()
    if len(contents) > _MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the 20 MB limit ({len(contents) // (1024*1024)} MB uploaded).",
        )
    await file.seek(0)

    file_path: Path = save_upload_file(file)

    document = Document(
        user_id=current_user.id,
        filename=file.filename,
        status=DocumentStatus.processing,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    background_tasks.add_task(_run_pipeline, document.id, file_path)

    return {
        "document_id": str(document.id),
        "status": document.status,
        "message": "Document uploaded. Processing started.",
    }


@router.get("/{document_id}")
def get_document_status(
    document_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Poll processing status and result for a document."""
    doc = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id)
        .first()
    )
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    return {
        "document_id": str(doc.id),
        "status": doc.status,
        "filename": doc.filename,
        "language": doc.language,
        "pages": doc.pages,
        "characters": doc.characters,
        "ocr_used": doc.ocr_used,
        "extracted_text": doc.extracted_text,
        "translated_text": doc.translated_text,
        "summary": doc.summary,
        "error": doc.error,
    }
