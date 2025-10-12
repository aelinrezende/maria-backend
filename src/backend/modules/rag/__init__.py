"""Módulo RAG (Retrieval-Augmented Generation) para busca semântica."""

from backend.modules.rag.rag_dto import (
    RAGQueryRequest,
    RAGStreamChunk,
    SourceEvaluationResult,
)
from backend.modules.rag.rag_enum import RAGChunkKind
from backend.modules.rag.rag_router import RAGRouter, rag_router
from backend.modules.rag.rag_service import RAGService

__all__ = [
    "RAGQueryRequest",
    "RAGStreamChunk",
    "SourceEvaluationResult",
    "RAGChunkKind",
    "RAGRouter",
    "rag_router",
    "RAGService",
]
