"""
Import all SQLAlchemy models.

Importing this module registers every model with Base.metadata.
"""

from app.models.user import User
from app.models.document import Document

__all__ = [
    "User",
    "Document",
]