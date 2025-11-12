"""Tipos de enumeração para o módulo RAG."""

from enum import Enum


class RAGChunkKind(str, Enum):
    """Tipos de chunks emitidos pelo serviço RAG."""
    START = "START"
    CONTENT = "CONTENT"
    SOURCES = "SOURCES"
    FINAL = "FINAL"
