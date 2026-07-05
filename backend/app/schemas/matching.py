from typing import Literal
from pydantic import BaseModel


class MatchRequest(BaseModel):
    job_description: str


class FieldComparison(BaseModel):
    field: str
    jd_value: str | None
    resume_value: str | None
    status: Literal["match", "partial", "missing", "not_specified"]
    detail: str | None = None


class MatchResponse(BaseModel):
    match_score: float          # 0.0 – 1.0
    matched: int
    partial: int
    missing: int
    comparisons: list[FieldComparison]
