from pydantic import BaseModel, Field


class TranslationRequest(BaseModel):
    text: str = Field(..., min_length=1)
    source_language: str = "auto"
    target_language: str = "en"


class TranslationResponse(BaseModel):
    source_language: str
    target_language: str = "en"
    translated_text: str
    translation_available: bool
