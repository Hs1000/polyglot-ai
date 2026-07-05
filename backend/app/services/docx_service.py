"""
DOCX processing service.
"""

from pathlib import Path

from docx import Document


class DOCXService:

    @staticmethod
    def extract_text(file_path: Path) -> dict:

        document = Document(file_path)

        paragraphs = []

        for paragraph in document.paragraphs:

            if paragraph.text.strip():

                paragraphs.append(paragraph.text)

        text = "\n".join(paragraphs)

        return {
            "text": text,
            "pages": 1,
            "characters": len(text),
            "metadata": {},
            "ocr_required": False,
        }