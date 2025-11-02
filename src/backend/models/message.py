from typing import TYPE_CHECKING, List

from sqlalchemy import Column, Enum, Index
from sqlmodel import Field, Relationship

from backend.models.base import BaseModel
from backend.models.message_chunk import MessageChunk
from backend.modules.message.message_enums import MessageRole

if TYPE_CHECKING:
    from backend.models.chunk import Chunk
    from backend.models.user import User


class Message(BaseModel, table=True):
    """Modelo de mensagem para histórico de conversas"""

    # Relacionamentos
    # Nulo para mensagens do sistema
    user_id: str = Field(
        nullable=True,
        foreign_key="user.id",
        ondelete="CASCADE"
    )
    user: "User" = Relationship(back_populates="messages")

    # Relacionamento N:N com chunks (fontes utilizadas)
    message_chunks: List["MessageChunk"] = Relationship(
        back_populates="message", cascade_delete=True
    )
    chunks: List["Chunk"] = Relationship(
        back_populates="messages",
        link_model=MessageChunk,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    # Campos básicos
    # Conteúdo criptografado
    content: str = Field(nullable=False, max_length=10000)
    author_role: MessageRole = Field(
        sa_column=Column(Enum(MessageRole), nullable=False)
    )

    # Índices otimizados para performance
    __table_args__ = (
        Index("ix_message_user_created", "user_id", "created_at"),
        Index("ix_message_author_role", "author_role"),
    )
