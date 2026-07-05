"""
Language Detection Service.
"""

from langdetect import detect

class LanguageService:

    @staticmethod
    def detect_language(
        text: str,
    ) -> str:

        if not text.strip():
            return "unknown"

        try:

            return detect(text)

        except Exception:

            return "unknown"