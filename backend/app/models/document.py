"""
Document model.
"""

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, Enum
import enum


class DocumentStatus(str, enum.Enum):
    processing = "processing"
    done = "done"
    failed = "failed"
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseEntity


class Document(BaseEntity):
    __tablename__ = "documents"

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default=DocumentStatus.processing,
        nullable=False,
    )

    error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    language: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    pages: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    characters: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    ocr_used: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    extracted_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    translated_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    user = relationship(
        "User",
        back_populates="documents",
    )

    def __repr__(self):
        return f"<Document {self.filename}>"