from pydantic import BaseModel


class ExtractionResponse(BaseModel):
    document_type: str
    fields: dict[str, str | None]
