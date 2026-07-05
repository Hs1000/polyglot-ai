"""
Document API.

Endpoints
---------
POST    /documents
GET     /documents
GET     /documents/{document_id}
DELETE  /documents/{document_id}
"""

from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.document import DocumentSummary
from app.services.document_service import DocumentService
from db.postgres import get_db


router = APIRouter()

document_service = DocumentService()


# ==========================================================
# Upload Document
# ==========================================================

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Upload and process a document.
    """

    try:

        return document_service.upload_document(
            db=db,
            file=file,
            current_user=current_user,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


# ==========================================================
# Get All Documents
# ==========================================================

@router.get("/", response_model=list[DocumentSummary])
def get_documents(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Return all documents for the logged in user.
    """

    return document_service.get_documents(
        db=db,
        current_user=current_user,
    )


# ==========================================================
# Get One Document
# ==========================================================

@router.get("/{document_id}", response_model=DocumentSummary)
def get_document(
    document_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Return one document.
    """

    try:

        return document_service.get_document(
            db=db,
            document_id=document_id,
            current_user=current_user,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


# ==========================================================
# Delete Document
# ==========================================================

@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(
    document_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Delete a document.
    """

    try:

        document_service.delete_document(
            db=db,
            document_id=document_id,
            current_user=current_user,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )