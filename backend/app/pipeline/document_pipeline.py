"""
Document Processing Pipeline.

Responsibilities
----------------
- Determine document type
- Extract text
- Detect language
- Translate if required
- Summarize
"""

from pathlib import Path

from app.services.docx_service import DOCXService
from app.services.language_service import LanguageService
from app.services.ocr_service import OCRService
from app.services.pdf_service import PDFService
from app.services.summary_service import SummaryService
from app.services.translation_service import TranslationService


class DocumentPipeline:
    """
    Main orchestration class for document processing.
    """

    def __init__(self):

        self.pdf_service = PDFService()
        self.docx_service = DOCXService()
        self.ocr_service = OCRService()
        self.language_service = LanguageService()
        self.translation_service = TranslationService()
        self.summary_service = SummaryService()

    def process(
        self,
        file_path: Path,
        target_language: str = "English",
    ) -> dict:
        """
        Process a document end-to-end.
        """

        extension = file_path.suffix.lower()

        # ----------------------------------------
        # Extract text
        # ----------------------------------------

        if extension == ".pdf":

            result = self.pdf_service.extract_text(
                file_path
            )

        elif extension == ".docx":

            result = self.docx_service.extract_text(
                file_path
            )

        else:

            raise ValueError(
                f"Unsupported file type: {extension}"
            )

        # ----------------------------------------
        # OCR
        # ----------------------------------------

        if result["ocr_required"]:

            result["text"] = self.ocr_service.extract_text(
                file_path
            )

            result["characters"] = len(result["text"])

        result["text"] = self.summary_service.clean_text(
            result["text"]
        )

        result["characters"] = len(result["text"])

        # ----------------------------------------
        # Language Detection
        # ----------------------------------------

        language = (
            self.language_service.detect_language(
                result["text"]
            )
        )

        # ----------------------------------------
        # Translation
        # ----------------------------------------

        translated_text = result["text"]

        if (
            language.lower() != "en"
            and language.lower() != "english"
        ):

            translated_text = (
                self.translation_service.translate(
                    translated_text,
                    source_lang=language,
                )
            )

        # ----------------------------------------
        # Summary
        # ----------------------------------------

        summary = self.summary_service.summarize(
            translated_text
        )

        # ----------------------------------------
        # Response
        # ----------------------------------------

        return {
            "filename": file_path.name,
            "pages": result["pages"],
            "characters": result["characters"],
            "language": language,
            "ocr_used": result["ocr_required"],
            "metadata": result["metadata"],
            "text": result["text"],
            "translated_text": translated_text,
            "summary": summary,
        }
