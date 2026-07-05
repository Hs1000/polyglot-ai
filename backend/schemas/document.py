from pydantic import BaseModel


class DocumentResponse(BaseModel):
    filename: str
    file_type: str
    pages: int
    language: str
    language_code: str
    ocr_used: bool
    characters: int
    preview: str
    text: str