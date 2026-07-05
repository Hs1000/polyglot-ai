from pathlib import Path

from services.pdf_service import PDFService
from services.docx_service import DOCXService
from services.image_service import ImageService
from services.ocr_service import OCRService


class RouterAgent:

    @staticmethod
    def process(file_path):

        extension = Path(file_path).suffix.lower()

        if extension == ".pdf":
            return PDFService.extract_text(file_path)

        if extension == ".docx":
            return DOCXService.extract_text(file_path)

        if extension == ".txt":
            with open(file_path, encoding="utf-8") as f:
                return {
                    "text": f.read(),
                    "pages": 1
                }

        if extension in [".png", ".jpg", ".jpeg"]:
            ImageService.load(file_path)

            return {
                "text": OCRService.extract_text(file_path),
                "pages": 1,
                "ocr": True
            }

        raise Exception("Unsupported file")