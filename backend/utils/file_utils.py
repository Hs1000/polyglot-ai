from pathlib import Path


SUPPORTED_TYPES = {
    ".pdf",
    ".docx",
    ".txt",
    ".png",
    ".jpg",
    ".jpeg"
}


def get_extension(filename: str):
    return Path(filename).suffix.lower()


def is_supported(filename: str):
    return get_extension(filename) in SUPPORTED_TYPES