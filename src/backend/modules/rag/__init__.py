"""Módulo RAG (Retrieval-Augmented Generation) para busca semântica."""

from backend.modules.rag.rag_dto import (
    RAGQueryRequest,
    RAGStreamChunk,
)
from backend.modules.rag.rag_enum import RAGChunkKind
from backend.modules.rag.rag_router import RAGRouter, rag_router
from backend.modules.rag.rag_service import RAGService

__all__ = [
    "RAGQueryRequest",
    "RAGStreamChunk",
    "RAGChunkKind",
    "RAGRouter",
    "rag_router",
    "RAGService",
]
