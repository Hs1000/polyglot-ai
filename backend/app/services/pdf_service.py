"""
PDF processing service.

Responsibilities
----------------
- Extract text from PDF
- Extract metadata
- Detect scanned PDFs
"""

from pathlib import Path
import fitz

class PDFService:
    """
    Service for processing PDF documents.
    """

    @staticmethod
    def extract_text(file_path: Path) -> dict:
        """
        Extract text and metadata from a PDF.
        """

        document = fitz.open(file_path)

        extracted_pages = []
        total_characters = 0

        for page in document:

            text = page.get_text("text")

            extracted_pages.append(text)

            total_characters += len(text)

        metadata = document.metadata or {}

        document.close()

        full_text = "\n".join(extracted_pages).strip()

        return {
            "text": full_text,
            "pages": len(extracted_pages),
            "characters": total_characters,
            "metadata": metadata,
            "ocr_required": total_characters == 0,
        }