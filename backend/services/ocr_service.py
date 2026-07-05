import easyocr


class OCRService:
    _latin_reader = None
    _cjk_reader = None

    @classmethod
    def _latin(cls):
        if cls._latin_reader is None:
            cls._latin_reader = easyocr.Reader(["en", "hi", "fr", "de", "es"], gpu=False)
        return cls._latin_reader

    @classmethod
    def _cjk(cls):
        if cls._cjk_reader is None:
            # ch_sim, ja, ko are each only compatible with English in easyocr
            cls._cjk_reader = easyocr.Reader(["ch_sim", "en"], gpu=False)
        return cls._cjk_reader

    @classmethod
    def extract_text(cls, image_path):
        latin_items = cls._latin().readtext(image_path)
        latin_text = " ".join(item[1] for item in latin_items)

        cjk_items = cls._cjk().readtext(image_path)
        cjk_text = " ".join(item[1] for item in cjk_items)

        return cjk_text if len(cjk_text) > len(latin_text) else latin_text
