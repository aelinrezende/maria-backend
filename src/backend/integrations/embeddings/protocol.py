from __future__ import annotations

from typing import Iterable, List, Protocol


class EmbeddingProvider(Protocol):
    """Contrato mínimo para provedores de embeddings (API assíncrona).

    Todos os métodos retornam listas de vetores float (uma lista por texto),
    executando possivelmente trabalho pesado em thread pool.
    """

    async def embed(self, texts: Iterable[str]) -> List[List[float]]:
        """Gera embeddings (sem prefixos específicos)."""

    async def embed_queries(self, texts: Iterable[str]) -> List[List[float]]:
        """Gera embeddings de consultas aplicando prefixo 'query: '."""

    async def embed_passages(self, texts: Iterable[str]) -> List[List[float]]:
        """Gera embeddings de passagens/documentos aplicando prefixo 'passage: '."""
