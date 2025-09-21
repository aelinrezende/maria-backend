"""DTOs para operações RAG (Retrieval-Augmented Generation)."""

from typing import List, Optional

from sqlmodel import Field, SQLModel


class RAGQueryRequest(SQLModel):
    """Payload para consulta RAG."""

    query: str = Field(min_length=1, max_length=1000,
                       description="Pergunta do usuário")


class ChunkResult(SQLModel):
    """Resultado de um chunk encontrado na busca."""

    chunk_id: str = Field(description="ID do chunk")
    content: str = Field(description="Conteúdo do chunk")
    document_title: Optional[str] = Field(
        default=None, description="Título do documento")
    document_source: Optional[str] = Field(
        default=None, description="Fonte do documento")


class RAGQueryResponse(SQLModel):
    """Resposta da consulta RAG."""

    query: str = Field(description="Pergunta original do usuário")
    chunks_found: int = Field(description="Número de chunks encontrados")
    chunks: List[ChunkResult] = Field(description="Lista de chunks relevantes")
    processing_time_sec: Optional[float] = Field(
        default=None, description="Tempo de processamento em segundos")
