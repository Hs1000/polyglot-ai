"""
Document Service.

Business logic for document management.

Responsibilities
----------------
- Upload document
- Process document
- Save document
- Retrieve documents
- Delete documents
"""

from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.user import User
from app.pipeline.document_pipeline import DocumentPipeline
from app.utils.file_utils import save_upload_file


class DocumentService:
    """
    Service responsible for all document operations.
    """

    def __init__(self):

        self.pipeline = DocumentPipeline()

    # ==========================================================
    # Upload
    # ==========================================================

    def upload_document(
        self,
        db: Session,
        file: UploadFile,
        current_user: User,
    ) -> dict:
        """
        Upload and process a document.
        """

        # Save uploaded file
        file_path: Path = save_upload_file(file)

        # Process document
        result = self.pipeline.process(file_path)

        # Store in database
        document = Document(
            user_id=current_user.id,
            filename=result["filename"],
            language=result["language"],
            pages=result["pages"],
            characters=result["characters"],
            ocr_used=result["ocr_used"],
            extracted_text=result["text"],
            translated_text=result["translated_text"],
            summary=result["summary"],
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return {
            "message": "Document processed successfully.",
            "document_id": str(document.id),
            "document": document,
            "result": result,
        }

    # ==========================================================
    # Get All Documents
    # ==========================================================

    def get_documents(
        self,
        db: Session,
        current_user: User,
    ) -> list[Document]:
        """
        Return all documents owned by the current user.
        """

        return (
            db.query(Document)
            .filter(
                Document.user_id == current_user.id
            )
            .order_by(
                Document.created_at.desc()
            )
            .all()
        )

    # ==========================================================
    # Get Single Document
    # ==========================================================

    def get_document(
        self,
        db: Session,
        document_id,
        current_user: User,
    ) -> Document:
        """
        Return one document.
        """

        document = (
            db.query(Document)
            .filter(
                Document.id == document_id,
                Document.user_id == current_user.id,
            )
            .first()
        )

        if document is None:
            raise ValueError(
                "Document not found."
            )

        return document

    # ==========================================================
    # Delete Document
    # ==========================================================

    def delete_document(
        self,
        db: Session,
        document_id,
        current_user: User,
    ) -> None:
        """
        Delete a document.
        """

        document = self.get_document(
            db=db,
            document_id=document_id,
            current_user=current_user,
        )

        db.delete(document)

        db.commit()