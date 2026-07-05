import os
import shutil

from fastapi import APIRouter, UploadFile

from agents.router_agent import RouterAgent
from services.language_service import LanguageService

router = APIRouter()

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_document(file: UploadFile):

    path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = RouterAgent.process(path)

    language = LanguageService.detect(result["text"])

    return {
        "filename": file.filename,
        "file_type": file.filename.split(".")[-1],
        "pages": result["pages"],
        "language": language["language"],
        "language_code": language["code"],
        "ocr_used": result.get("ocr", False),
        "characters": len(result["text"]),
        "preview": result["text"][:500],
        "text": result["text"]
    }
