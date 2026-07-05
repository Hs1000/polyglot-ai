import fitz

class PDFService:

    @staticmethod
    def extract_text(file_path: str):

        document = fitz.open(file_path)

        pages = len(document)

        text = ""

        for page in document:
            text += page.get_text()

        document.close()

        return {
            "text": text,
            "pages": pages
        }