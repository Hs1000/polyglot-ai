from docx import Document

class DOCXService:

    @staticmethod
    def extract_text(file_path):

        doc = Document(file_path)

        text = "\n".join(
            paragraph.text
            for paragraph in doc.paragraphs
        )

        return {
            "text": text,
            "pages": 1
        }