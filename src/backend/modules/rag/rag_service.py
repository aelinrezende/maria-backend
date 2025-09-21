"""Serviço para operações RAG (Retrieval-Augmented Generation)."""

import time

from fastapi.params import Depends
from sqlalchemy.orm import selectinload
from wireup import service

from backend.integrations.embeddings import LocalSentenceTransformerProvider
from backend.models.chunk import Chunk
from backend.modules.chunk.chunk_repository import ChunkRepository
from backend.modules.rag.rag_dto import ChunkResult, RAGQueryRequest, RAGQueryResponse


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

    async def query_rag_stream(self, request: RAGQueryRequest) -> RAGQueryResponse:
        """
        Realiza consultas RAG com streaming de respostas.

        Args:
            request: Requisição com query

        Returns:
            Streaming da resposta gerada
        """
        start_time = time.time()

        query_embedding, *_ = await self.embeddings.embed_queries([request.query])

        similar_chunks = await self.chunk_repository.get_similar(
            query_embedding,
            builder=lambda query: query.options(
                selectinload(Chunk.document)
            ),
        )

        chunk_results = [
            ChunkResult(
                chunk_id=chunk.id,
                content=chunk.content,
                document_title=chunk.document.title,
                document_source=chunk.document.source
            ) for chunk in similar_chunks
        ]

        processing_time = time.time() - start_time

        # TODO: Integrar com o modelo de linguagem para gerar resposta baseada nos chunks
        # response = await self.provider.stream_chat(...)

        # TODO: Implementar streaming de resposta
        return RAGQueryResponse(
            query=request.query,
            chunks_found=len(chunk_results),
            chunks=chunk_results,
            processing_time_sec=processing_time
        )
