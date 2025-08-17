from __future__ import annotations

from typing import Iterable, List, Sequence

from anyio import to_thread
from loguru import logger
from sentence_transformers import SentenceTransformer
from wireup import service

from backend.core.config import settings

from .protocol import EmbeddingProvider


@service(lifetime="singleton")
class LocalSentenceTransformerProvider(EmbeddingProvider):
    """Provider de embeddings baseado em sentence-transformers.

    Carrega uma única instância do modelo (singleton) e expõe métodos para
    gerar embeddings genéricos (embed), de consultas (embed_queries) e
    de passagens/documentos (embed_passages) aplicando os prefixos E5.

    Usa-se o offload para thread pool (to_thread.run_sync) para não bloquear o loop.
    """

    def __init__(self):
        """Carrega o modelo definido em settings.EMBEDDING_MODEL."""
        logger.info(
            f"Carregando modelo de embeddings: {settings.EMBEDDING_MODEL}"
        )

        self.model_name = settings.EMBEDDING_MODEL
        self._model = SentenceTransformer(self.model_name)

    def _encode(self, batch: Sequence[str]) -> List[List[float]]:
        """Codifica uma sequência de textos já preparados retornando lista de vetores."""
        if not batch:
            return []

        vectors = self._model.encode(
            batch, show_progress_bar=False, normalize_embeddings=True
        )

        return [vector.tolist() for vector in vectors]

    async def embed(self, texts: Iterable[str]) -> List[List[float]]:
        """Embeddings diretos (sem prefixos) para uso genérico ou testes."""
        return await to_thread.run_sync(self._encode, list(texts))

    async def embed_queries(self, texts: Iterable[str]) -> List[List[float]]:
        """Embeddings de consultas aplicando prefixo 'query: '."""
        return await to_thread.run_sync(
            self._encode, [f"query: {text}" for text in texts]
        )

    async def embed_passages(self, texts: Iterable[str]) -> List[List[float]]:
        """Embeddings de passagens/documentos aplicando prefixo 'passage: '."""
        return await to_thread.run_sync(
            self._encode, [f"passage: {text}" for text in texts]
        )
