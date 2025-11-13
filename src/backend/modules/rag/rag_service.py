"""Serviço para operações RAG (Retrieval-Augmented Generation)."""

import asyncio
from typing import AsyncGenerator

from fastapi.params import Depends
from wireup import service

from backend.integrations.embeddings import LocalSentenceTransformerProvider
from backend.integrations.llm import LLMFactory
from backend.modules.chunk.chunk_repository import ChunkRepository
from backend.modules.rag import handlers
from backend.modules.rag.rag_dto import RAGQueryRequest, RAGStreamChunk
from backend.modules.rag.rag_enum import RAGChunkKind


@service(lifetime="scoped")
class RAGService:
    """Serviço para consultas RAG com busca semântica."""

    def __init__(
        self,
        embeddings: LocalSentenceTransformerProvider = Depends(),
        chunk_repository: ChunkRepository = Depends()
    ):
        self.embeddings = embeddings
        self.chunk_repository = chunk_repository
        self.llm_provider = LLMFactory.create_provider()

    async def query_rag_stream(self, request: RAGQueryRequest) -> AsyncGenerator[str, None]:
        """
        Realiza consultas RAG com streaming de respostas em tempo real.

        Args:
            request: Requisição com query

        Yields:
            RAGStreamChunk: Chunks da resposta com fontes conforme são gerados pelo LLM
        """
        # Envia um sinal de início para estabelecer a stream
        yield RAGStreamChunk(kind=RAGChunkKind.START).streamed
        await asyncio.sleep(0)  # Force flush

        # Verifica se deve pular o RAG (consulta direta ao LLM)
        skip_rag: bool = await handlers.should_skip_rag(self, request.query)

        if skip_rag:
            async for chunk in handlers.generate_direct_response(self, request.query):
                yield chunk

            return

        async for chunk in handlers.orchestrate_rag(self, request.query):
            yield chunk
