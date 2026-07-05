"""
Utility functions for file handling.

Responsibilities:
- Validate uploaded files
- Save uploaded files
- Generate unique filenames
- Delete uploaded files
"""

from pathlib import Path
from uuid import uuid4
import shutil

from fastapi import HTTPException, UploadFile


# ==========================================
# Configuration
# ==========================================

UPLOAD_DIRECTORY = Path("app/uploads")

UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".png",
    ".jpg",
    ".jpeg",
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


# ==========================================
# Validation
# ==========================================

def get_extension(filename: str) -> str:
    """Return lowercase file extension."""

    return Path(filename).suffix.lower()


def validate_extension(filename: str) -> None:
    """Validate supported file extension."""

    extension = get_extension(filename)

    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {extension}",
        )


# ==========================================
# Filename Generation
# ==========================================

def generate_filename(filename: str) -> str:
    """
    Generate a unique filename.

    Example:
    research.pdf

    becomes

    a73h72g1-research.pdf
    """

    extension = get_extension(filename)

    unique_id = uuid4().hex

    return f"{unique_id}{extension}"


# ==========================================
# Save File
# ==========================================

def save_upload_file(file: UploadFile) -> Path:
    """
    Save uploaded file to uploads directory.

    Returns
    -------
    Path
        Absolute path of saved file.
    """

    validate_extension(file.filename)

    filename = generate_filename(file.filename)

    destination = UPLOAD_DIRECTORY / filename

    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return destination


# ==========================================
# Delete File
# ==========================================

def delete_file(path: Path) -> None:
    """Delete uploaded file."""

    if path.exists():
        path.unlink()


# ==========================================
# File Metadata
# ==========================================

def get_file_metadata(path: Path) -> dict:
    """
    Return basic file metadata.
    """

    return {
        "filename": path.name,
        "extension": path.suffix.lower(),
        "size": path.stat().st_size,
    }