from typing import TYPE_CHECKING, Any, List

from pgvector.sqlalchemy import Vector
from sqlmodel import Field, Relationship

from backend.core import settings
from backend.models.base import BaseModel
from backend.models.message_chunk import MessageChunk

if TYPE_CHECKING:
    from backend.models.document import Document
    from backend.models.message import Message


class Chunk(BaseModel, table=True):
    """Modelo para fragmentos de documentos na base de conhecimento"""

    # Relacionamentos
    document: "Document" = Relationship(
        back_populates="chunks"
    )
    document_id: str = Field(
        nullable=False, foreign_key="document.id", ondelete="CASCADE"
    )

    # Relacionamento N:N com mensagens (quais mensagens usaram este chunk)
    message_chunks: List["MessageChunk"] = Relationship(
        back_populates="chunk", cascade_delete=True
    )
    messages: List["Message"] = Relationship(
        back_populates="chunks",
        link_model=MessageChunk,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    # Informações básicas
    content: str = Field(nullable=False, max_length=10000)
    embedding: Any = Field(
        nullable=False, sa_type=Vector(settings.EMBEDDING_DIMENSION)
    )
    size: int = Field(nullable=False)
    order: int = Field(nullable=False)
    page: int = Field(nullable=False)
