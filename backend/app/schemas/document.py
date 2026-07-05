from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UploadResponse(BaseModel):
    status: str
    filename: str
    file_type: str
    message: str


class DocumentMetadata(BaseModel):
    language: Optional[str] = None
    language_code: Optional[str] = None
    pages: Optional[int] = None
    characters: Optional[int] = None
    ocr_used: bool = False


class SummaryResponse(BaseModel):
    filename: str
    metadata: DocumentMetadata
    preview: str
    translated_text: Optional[str] = None
    summary: Optional[str] = None


class DocumentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    status: str
    language: Optional[str] = None
    pages: Optional[int] = None
    characters: Optional[int] = None
    ocr_used: bool
    summary: Optional[str] = None
    translated_text: Optional[str] = None
    extracted_text: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime