from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from backend.models.chunk import Chunk
    from backend.models.message import Message


class MessageChunk(SQLModel, table=True):
    """Modelo de associação para relacionamento N:N entre Message e Chunk"""

    __tablename__ = "message_chunk"

    message_id: str = Field(
        foreign_key="message.id", primary_key=True, ondelete="CASCADE"
    )
    chunk_id: str = Field(
        foreign_key="chunk.id", primary_key=True, ondelete="CASCADE"
    )

    # Relacionamentos
    message: "Message" = Relationship(back_populates="message_chunks")
    chunk: "Chunk" = Relationship(back_populates="message_chunks")
