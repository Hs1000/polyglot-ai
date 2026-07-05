from langdetect import detect


LANGUAGE_MAP = {
    "en": "English",
    "hi": "Hindi",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "ja": "Japanese",
    "zh-cn": "Chinese",
    "ko": "Korean"
}


class LanguageService:

    @staticmethod
    def detect(text):

        code = detect(text)

        return {
            "code": code,
            "language": LANGUAGE_MAP.get(
                code,
                code
            )
        }