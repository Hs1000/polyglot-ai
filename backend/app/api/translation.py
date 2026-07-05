"""
Translation API.

Endpoints
---------
POST /translate — translate text into English
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.translation import TranslationRequest, TranslationResponse
from app.services.language_service import LanguageService
from app.services.translation_service import TranslationService


router = APIRouter()

language_service = LanguageService()
translation_service = TranslationService()


@router.post("/", response_model=TranslationResponse)
def translate_text(
    payload: TranslationRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Translate user-provided text into English.
    """

    text = payload.text.strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text is required.",
        )

    source_language = payload.source_language.lower().strip()
    target_language = payload.target_language.lower().strip() or "en"

    if source_language == "auto":
        source_language = language_service.detect_language(text)

    if source_language == target_language:
        return TranslationResponse(
            source_language=source_language,
            target_language=target_language,
            translated_text=text,
            translation_available=True,
        )

    translation_available = translation_service.supports_pair(source_language, target_language)
    translated_text = translation_service.translate(
        text,
        source_lang=source_language,
        target_lang=target_language,
    )

    return TranslationResponse(
        source_language=source_language,
        target_language=target_language,
        translated_text=translated_text,
        translation_available=translation_available,
    )
