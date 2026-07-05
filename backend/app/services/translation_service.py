"""
Translation Service.

Uses facebook/nllb-200-distilled-1.3B — a single HuggingFace model that
supports 200+ languages. The model (~2.4 GB) is downloaded on first use.

Short-input token budget: for 1-3 word inputs the output is capped tightly
(words + 2 tokens) so the model cannot hallucinate extra context.
"""

import logging
import re

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FLORES-200 language codes required by NLLB
# ---------------------------------------------------------------------------

_NLLB_CODES: dict[str, str] = {
    "af":    "afr_Latn",
    "ar":    "arb_Arab",
    "de":    "deu_Latn",
    "en":    "eng_Latn",
    "es":    "spa_Latn",
    "fr":    "fra_Latn",
    "it":    "ita_Latn",
    "ja":    "jpn_Jpan",
    "ko":    "kor_Hang",
    "nl":    "nld_Latn",
    "pl":    "pol_Latn",
    "pt":    "por_Latn",
    "ru":    "rus_Cyrl",
    "sv":    "swe_Latn",
    "tr":    "tur_Latn",
    "uk":    "ukr_Cyrl",
    "zh":    "zho_Hans",
    "zh-cn": "zho_Hans",
    "zh-tw": "zho_Hant",
}

_SUPPORTED = set(_NLLB_CODES)
_CHUNK_CHARS = 800
MODEL_ID = "facebook/nllb-200-distilled-1.3B"


def _max_tokens(word_count: int) -> int:
    """Token budget scaled to input length to prevent hallucination."""
    if word_count <= 3:
        return word_count * 3 + 4
    return word_count * 3 + 10


# ---------------------------------------------------------------------------
# Single-word lookup table
# ---------------------------------------------------------------------------
# NLLB is trained on sentence pairs and cannot reliably translate isolated
# words — it treats them as sentence openers and hallucinates the implied
# rest. This dictionary covers the most common single-word inputs.
# Keys are lowercase. Source language → target language → word → translation.

_WORD_DICT: dict[str, dict[str, dict[str, str]]] = {
    "es": {
        "en": {
            "sí": "Yes", "si": "Yes", "no": "No", "hola": "Hello",
            "adiós": "Goodbye", "adios": "Goodbye", "gracias": "Thank you",
            "por favor": "Please", "perdón": "Sorry", "perdon": "Sorry",
            "disculpe": "Excuse me", "bien": "Good", "mal": "Bad",
            "bueno": "Good", "malo": "Bad", "quizás": "Maybe",
            "quizas": "Maybe", "tal vez": "Maybe", "amor": "Love",
            "amigo": "Friend", "casa": "House", "agua": "Water",
            "comida": "Food", "trabajo": "Work", "dinero": "Money",
            "tiempo": "Time", "hoy": "Today", "mañana": "Tomorrow",
            "ayer": "Yesterday", "noche": "Night", "día": "Day",
            "dia": "Day", "gato": "Cat", "perro": "Dog",
        },
    },
    "fr": {
        "en": {
            "oui": "Yes", "non": "No", "bonjour": "Hello",
            "salut": "Hi", "au revoir": "Goodbye", "merci": "Thank you",
            "s'il vous plaît": "Please", "svp": "Please",
            "pardon": "Sorry", "excusez-moi": "Excuse me",
            "bien": "Good", "mal": "Bad", "peut-être": "Maybe",
            "amour": "Love", "ami": "Friend", "maison": "House",
            "eau": "Water", "nourriture": "Food", "travail": "Work",
            "argent": "Money", "temps": "Time", "aujourd'hui": "Today",
            "demain": "Tomorrow", "hier": "Yesterday", "nuit": "Night",
            "jour": "Day", "chat": "Cat", "chien": "Dog",
        },
    },
    "de": {
        "en": {
            "ja": "Yes", "nein": "No", "hallo": "Hello", "tschüss": "Bye",
            "auf wiedersehen": "Goodbye", "danke": "Thank you",
            "bitte": "Please", "entschuldigung": "Sorry",
            "gut": "Good", "schlecht": "Bad", "vielleicht": "Maybe",
            "liebe": "Love", "freund": "Friend", "haus": "House",
            "wasser": "Water", "essen": "Food", "arbeit": "Work",
            "geld": "Money", "zeit": "Time", "heute": "Today",
            "morgen": "Tomorrow", "gestern": "Yesterday",
            "nacht": "Night", "tag": "Day", "katze": "Cat",
            "hund": "Dog",
        },
    },
    "it": {
        "en": {
            "sì": "Yes", "no": "No", "ciao": "Hello",
            "arrivederci": "Goodbye", "grazie": "Thank you",
            "per favore": "Please", "scusa": "Sorry",
            "bene": "Good", "male": "Bad", "forse": "Maybe",
            "amore": "Love", "amico": "Friend", "casa": "House",
            "acqua": "Water", "cibo": "Food", "lavoro": "Work",
            "soldi": "Money", "tempo": "Time", "oggi": "Today",
            "domani": "Tomorrow", "ieri": "Yesterday",
            "notte": "Night", "giorno": "Day", "gatto": "Cat",
            "cane": "Dog",
        },
    },
    "pt": {
        "en": {
            "sim": "Yes", "não": "No", "nao": "No", "olá": "Hello",
            "ola": "Hello", "tchau": "Bye", "obrigado": "Thank you",
            "obrigada": "Thank you", "por favor": "Please",
            "desculpe": "Sorry", "bom": "Good", "mau": "Bad",
            "talvez": "Maybe", "amor": "Love", "amigo": "Friend",
            "casa": "House", "água": "Water", "agua": "Water",
            "comida": "Food", "trabalho": "Work", "dinheiro": "Money",
            "tempo": "Time", "hoje": "Today", "amanhã": "Tomorrow",
            "amanha": "Tomorrow", "ontem": "Yesterday",
            "noite": "Night", "dia": "Day", "gato": "Cat",
            "cachorro": "Dog",
        },
    },
    "ru": {
        "en": {
            "да": "Yes", "нет": "No", "привет": "Hello",
            "пока": "Bye", "до свидания": "Goodbye",
            "спасибо": "Thank you", "пожалуйста": "Please",
            "извините": "Sorry", "хорошо": "Good", "плохо": "Bad",
            "может быть": "Maybe", "любовь": "Love", "друг": "Friend",
            "дом": "House", "вода": "Water", "еда": "Food",
            "работа": "Work", "деньги": "Money", "время": "Time",
            "сегодня": "Today", "завтра": "Tomorrow",
            "вчера": "Yesterday", "ночь": "Night", "день": "Day",
            "кошка": "Cat", "собака": "Dog",
        },
    },
    "en": {
        "es": {
            "yes": "Sí", "no": "No", "hello": "Hola", "hi": "Hola",
            "bye": "Adiós", "goodbye": "Adiós",
            "good morning": "Buenos días", "good night": "Buenas noches",
            "good evening": "Buenas tardes", "good afternoon": "Buenas tardes",
            "thank you": "Gracias",
            "thanks": "Gracias", "please": "Por favor", "sorry": "Lo siento",
            "good": "Bueno", "bad": "Malo", "maybe": "Tal vez",
            "love": "Amor", "friend": "Amigo", "house": "Casa",
            "water": "Agua", "food": "Comida", "work": "Trabajo",
            "money": "Dinero", "today": "Hoy", "tomorrow": "Mañana",
            "yesterday": "Ayer", "night": "Noche", "day": "Día",
            "cat": "Gato", "dog": "Perro",
        },
        "fr": {
            "yes": "Oui", "no": "Non", "hello": "Bonjour", "hi": "Salut",
            "bye": "Au revoir", "goodbye": "Au revoir",
            "good morning": "Bonjour", "good night": "Bonne nuit",
            "good evening": "Bonsoir", "good afternoon": "Bon après-midi",
            "thank you": "Merci", "thanks": "Merci",
            "please": "S'il vous plaît", "sorry": "Pardon",
            "good": "Bien", "bad": "Mal", "maybe": "Peut-être",
            "love": "Amour", "friend": "Ami", "house": "Maison",
            "water": "Eau", "food": "Nourriture", "work": "Travail",
            "money": "Argent", "today": "Aujourd'hui",
            "tomorrow": "Demain", "yesterday": "Hier",
            "night": "Nuit", "day": "Jour", "cat": "Chat",
            "dog": "Chien",
        },
        "de": {
            "yes": "Ja", "no": "Nein", "hello": "Hallo", "hi": "Hallo",
            "bye": "Tschüss", "goodbye": "Auf Wiedersehen",
            "good morning": "Guten Morgen", "good night": "Gute Nacht",
            "good evening": "Guten Abend", "good afternoon": "Guten Tag",
            "thank you": "Danke", "thanks": "Danke",
            "please": "Bitte", "sorry": "Entschuldigung",
            "good": "Gut", "bad": "Schlecht", "maybe": "Vielleicht",
            "love": "Liebe", "friend": "Freund", "house": "Haus",
            "water": "Wasser", "food": "Essen", "work": "Arbeit",
            "money": "Geld", "today": "Heute", "tomorrow": "Morgen",
            "yesterday": "Gestern", "night": "Nacht", "day": "Tag",
            "cat": "Katze", "dog": "Hund",
        },
        "it": {
            "yes": "Sì", "no": "No", "hello": "Ciao", "hi": "Ciao",
            "bye": "Ciao", "goodbye": "Arrivederci",
            "good morning": "Buongiorno", "good night": "Buonanotte",
            "good evening": "Buonasera", "good afternoon": "Buon pomeriggio",
            "thank you": "Grazie", "thanks": "Grazie",
            "please": "Per favore", "sorry": "Scusa",
            "good": "Bene", "bad": "Male", "maybe": "Forse",
            "love": "Amore", "friend": "Amico", "house": "Casa",
            "water": "Acqua", "food": "Cibo", "work": "Lavoro",
            "money": "Soldi", "today": "Oggi", "tomorrow": "Domani",
            "yesterday": "Ieri", "night": "Notte", "day": "Giorno",
            "cat": "Gatto", "dog": "Cane",
        },
    },
}


def _lookup(text: str, src: str, tgt: str) -> str | None:
    """Return a dictionary translation for short known inputs, or None."""
    key = text.strip().lower().rstrip(".!?,;")
    return _WORD_DICT.get(src, {}).get(tgt, {}).get(key)


class TranslationService:

    def __init__(self):
        self._pipeline = None

    def _get_pipeline(self):
        if self._pipeline is None:
            from transformers import pipeline
            logger.info("Loading NLLB-200 model (first run — downloading ~2.4 GB)…")
            self._pipeline = pipeline("translation", model=MODEL_ID)
            logger.info("NLLB-200 model loaded.")
        return self._pipeline

    def supports_pair(self, source_lang: str, target_lang: str) -> bool:
        return (
            source_lang.lower() in _NLLB_CODES
            and target_lang.lower() in _NLLB_CODES
        )

    @staticmethod
    def supports_language(lang: str) -> bool:
        return lang.lower() in _SUPPORTED

    def translate(self, text: str, source_lang: str = "auto", target_lang: str = "en") -> str:
        if not text.strip():
            return ""

        src_code = _NLLB_CODES.get(source_lang.lower())
        tgt_code = _NLLB_CODES.get(target_lang.lower())

        if not src_code or not tgt_code:
            logger.warning("Unsupported language pair: %s → %s", source_lang, target_lang)
            return text

        # Fast path: single-word/short-phrase dictionary lookup.
        # NLLB cannot reliably translate isolated words without hallucinating
        # conversational context, so we short-circuit here for known entries.
        lookup = _lookup(text, source_lang.lower(), target_lang.lower())
        if lookup is not None:
            return lookup

        pipe = self._get_pipeline()
        chunks = self._chunk(text)

        translated = [
            pipe(
                chunk,
                src_lang=src_code,
                tgt_lang=tgt_code,
                max_new_tokens=_max_tokens(len(chunk.split())),
                num_beams=4,
                length_penalty=1.0,
                no_repeat_ngram_size=3,
            )[0]["translation_text"]
            for chunk in chunks
        ]
        return " ".join(translated)

    @staticmethod
    def _chunk(text: str) -> list[str]:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunks, current = [], ""
        for sent in sentences:
            if len(current) + len(sent) + 1 <= _CHUNK_CHARS:
                current = (current + " " + sent).strip()
            else:
                if current:
                    chunks.append(current)
                current = sent[:_CHUNK_CHARS]
        if current:
            chunks.append(current)
        return chunks or [text[:_CHUNK_CHARS]]
