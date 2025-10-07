"""DTOs para operações RAG (Retrieval-Augmented Generation)."""
from typing import List, Optional

from sqlmodel import Field, SQLModel

from backend.modules.base.base_dto import ModelBase
from backend.modules.rag.rag_enum import RAGChunkKind


class RAGQueryRequest(SQLModel):
    """Payload para consulta RAG."""

    query: str = Field(
        min_length=1,
        max_length=1000,
        description="Pergunta do usuário"
    )


class RAGStreamChunk(ModelBase):
    """Chunk individual de streaming com metadados."""
    content: Optional[str] = Field(
        default=None, description="Resposta gerada pela Mar.IA"
    )
    kind: RAGChunkKind = Field(description="Tipo do chunk")
    sources: Optional[List[str]] = Field(
        default=None, description="Lista de fontes dos documentos utilizados"
    )

    @property
    def streamed(self) -> str:
        """Formata o chunk para streaming no formato SSE."""
        return f"data: {self.model_dump(exclude_none=True)}\n\n"


class UserInputEvaluation(SQLModel):
    """Modelo para resposta de avaliação da entrada do usuário."""
    skip: bool
