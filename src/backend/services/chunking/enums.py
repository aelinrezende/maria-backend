"""Enumeração para estratégias de chunking."""
from enum import Enum


class ChunkingStrategy(str, Enum):
    """Estratégias disponíveis para chunking de texto."""

    PARAGRAPH = "PARAGRAPH"
    SENTENCE = "SENTENCE"
    SIZE = "SIZE"
