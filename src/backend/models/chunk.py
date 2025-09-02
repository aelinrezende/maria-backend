from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlmodel import Field, Relationship

from backend.core import settings
from backend.models.base import BaseModel

if TYPE_CHECKING:
    from backend.models.document import Document


class Chunk(BaseModel, table=True):
    """Modelo para fragmentos de documentos na base de conhecimento"""

    # Relacionamentos
    document: "Document" = Relationship(
        back_populates="chunks"
    )
    document_id: str = Field(
        nullable=False, foreign_key="document.id", ondelete="CASCADE"
    )

    # Informações básicas
    content: str = Field(nullable=False, max_length=10000)
    embedding: list[float] = Field(
        nullable=False, sa_type=Vector(settings.EMBEDDING_DIMENSION)
    )
    chunk_size: int = Field(nullable=False)
    chunk_order: int = Field(nullable=False)
