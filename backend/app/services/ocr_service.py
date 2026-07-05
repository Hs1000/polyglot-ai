"""
OCR Service.
"""

from pathlib import Path


# EasyOCR requires CJK scripts to be paired only with English.
_READER_GROUPS = [
    ["en", "fr", "de", "es", "hi", "ar"],  # Latin + Devanagari + Arabic
    ["ch_sim", "en"],                        # Simplified Chinese
    ["ch_tra", "en"],                        # Traditional Chinese
    ["ja", "en"],                            # Japanese
    ["ko", "en"],                            # Korean
]


class OCRService:

    def __init__(self):
        self._readers: dict = {}

    def _get_reader(self, index: int):
        if index not in self._readers:
            import easyocr  # lazy — avoids slow import at server startup
            self._readers[index] = easyocr.Reader(_READER_GROUPS[index])
        return self._readers[index]

    def extract_text(self, image_path: Path) -> str:
        best_text = ""

        for i in range(len(_READER_GROUPS)):
            try:
                reader = self._get_reader(i)
                result = reader.readtext(str(image_path))
                text = "\n".join(item[1] for item in result)
                if len(text) > len(best_text):
                    best_text = text
            except Exception:
                continue

        return best_text
