"""Serviço para operações RAG (Retrieval-Augmented Generation)."""

from typing import AsyncGenerator, List

from fastapi.params import Depends
from sqlalchemy.orm import selectinload
from wireup import service

from backend.constants import (
    RAG_CHUNK_CONTEXT_TEMPLATE,
    RAG_SYSTEM_PROMPT,
    RAG_USER_PROMPT_TEMPLATE,
)
from backend.integrations.embeddings import LocalSentenceTransformerProvider
from backend.integrations.llm import LLMFactory, Message
from backend.models.chunk import Chunk
from backend.modules.chunk.chunk_repository import ChunkRepository
from backend.modules.rag.rag_dto import (
    RAGQueryRequest,
    RAGStreamChunk,
)
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

    def _format_chunks_context(self, chunk_results: List[Chunk]) -> str:
        """
        Formata os chunks usando o template de contexto.

        Args:
            chunk_results: Lista de chunks encontrados

        Returns:
            Contexto formatado para o LLM
        """
        if not chunk_results:
            return ""

        formatted_chunks = [
            RAG_CHUNK_CONTEXT_TEMPLATE.format(
                chunk_number=i,
                document_title=chunk.document.title or "Documento sem título",
                document_source=chunk.document.source or "Fonte não disponível",
                chunk_content=chunk.content
            )
            for i, chunk in enumerate(chunk_results, 1)
        ]

        return "\n".join(formatted_chunks)

    async def query_rag_stream(self, request: RAGQueryRequest) -> AsyncGenerator[str, None]:
        """
        Realiza consultas RAG com streaming de respostas em tempo real.

        Args:
            request: Requisição com query

        Yields:
            RAGStreamChunk: Chunks da resposta com fontes conforme são gerados pelo LLM
        """
        # 1. Buscar chunks similares
        query_embedding, *_ = await self.embeddings.embed_queries([request.query])

        similar_chunks = await self.chunk_repository.get_similar(
            query_embedding,
            builder=lambda query: query.options(
                selectinload(Chunk.document)
            ),
        )

        # 2. Preparar prompt baseado na disponibilidade de chunks
        if similar_chunks:
            # Com contexto: usar template completo
            chunks_context = self._format_chunks_context(similar_chunks)
            user_prompt = RAG_USER_PROMPT_TEMPLATE.format(
                chunks_context=chunks_context,
                user_query=request.query
            )
        else:
            # Sem contexto: resposta dinâmica
            user_prompt = (
                f"Pergunta: {request.query}\n\n"
                f"Não encontrei documentos relevantes sobre este tópico."
            )

        # 3. Extrair fontes únicas dos documentos encontrados
        sources = list({
            chunk.document.source for chunk in similar_chunks
            if chunk.document.source
        })

        yield RAGStreamChunk(
            kind=RAGChunkKind.SOURCES,
            sources=sources
        ).streamed

        # 4. Gerar resposta com LLM em streaming
        llm_provider = LLMFactory.create_provider()

        messages = [Message(role="user", content=user_prompt)]

        # 5. Fazer yield dos chunks com fontes conforme chegam do LLM
        async for chunk in llm_provider.stream_chat(
            messages=messages,
            system_prompt=RAG_SYSTEM_PROMPT
        ):
            if chunk.content:
                yield RAGStreamChunk(
                    content=chunk.content,
                    kind=RAGChunkKind.CONTENT
                ).streamed

        yield RAGStreamChunk(kind=RAGChunkKind.FINAL).streamed
