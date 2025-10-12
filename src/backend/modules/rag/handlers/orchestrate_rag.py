
from typing import TYPE_CHECKING, AsyncGenerator, List

from loguru import logger
from sqlalchemy.orm import selectinload
from sqlmodel import col

from backend.constants.prompts import (
    RAG_CHUNK_CONTEXT_TEMPLATE,
    RAG_SYSTEM_PROMPT,
    RAG_USER_PROMPT_TEMPLATE,
)
from backend.integrations.llm.models import Message
from backend.models.chunk import Chunk
from backend.modules.rag import handlers
from backend.modules.rag.handlers.evaluate_sources import ChunkEvaluationCallback
from backend.modules.rag.rag_dto import RAGStreamChunk
from backend.modules.rag.rag_enum import RAGChunkKind

if TYPE_CHECKING:
    from backend.modules.rag.rag_service import RAGService


async def orchestrate_rag(
    hub: "RAGService",
    query: str
) -> AsyncGenerator[str, None]:
    """Orquestra o fluxo de RAG para uma requisição, retornando respostas em streaming.

    Passos:
    1. Gera embedding da query.
    2. Busca chunks similares no banco.
    3. Prepara prompt baseado na disponibilidade de chunks.
        1. Refinamento e estruturação dos chunks encontrados.
        2. Informa a ausência de contexto.
    4. Gera resposta com LLM em streaming.
    """
    logger.info(f"Iniciando orquestração RAG para query: {query}")

    # 1. Gerar embedding da query
    query_embedding, *_ = await hub.embeddings.embed_queries([query])

    # 2. Busca chunks similares com lógica de tentativas múltiplas
    async def callback(excluded_chunk_ids: List[int]) -> ChunkEvaluationCallback:
        chunks: List[Chunk] = await hub.chunk_repository.get_similar(
            query_embedding,
            builder=lambda query: query.where(col(Chunk.id).not_in(excluded_chunk_ids)).options(
                selectinload(Chunk.document)
            ),
        )

        evaluation = await handlers.evaluate_found_sources(hub, query, [c.content for c in chunks])

        return (chunks, evaluation)

    similar_chunks = await handlers.rag_chunk_evaluation(callback)

    # 3. Prepara prompt baseado na disponibilidade de chunks
    if similar_chunks:
        # 3.1 TODO: Refinamento e estruturação dos chunks encontrados
        user_prompt = RAG_USER_PROMPT_TEMPLATE.format(
            chunks_context=_format_chunks_context(similar_chunks),
            user_query=query
        )
    else:
        # 3.2 TODO: Informa a ausência de contexto
        user_prompt = (
            f"Pergunta: {query}\n\n"
            f"Não encontrei documentos relevantes sobre este tópico."
        )

    # Extrai fontes únicas dos documentos encontrados e faz yield como chunk separado
    sources = list(dict.fromkeys(
        chunk.document.source for chunk in similar_chunks
        if chunk.document.source
    ))

    yield RAGStreamChunk(
        kind=RAGChunkKind.SOURCES,
        sources=sources
    ).streamed

    # 4. Gera resposta com LLM em streaming
    messages = [Message(role="user", content=user_prompt)]

    async for chunk in hub.llm_provider.stream_chat(
        messages=messages,
        system_prompt=RAG_SYSTEM_PROMPT
    ):
        if chunk.content:
            yield RAGStreamChunk(
                content=chunk.content,
                kind=RAGChunkKind.CONTENT
            ).streamed

    yield RAGStreamChunk(kind=RAGChunkKind.FINAL).streamed


def _format_chunks_context(chunk_results: List[Chunk]) -> str:
    """
      Formata os chunks usando o template de contexto.

      Args:
          chunk_results: Lista de chunks encontrados

      Returns:
          Contexto formatado para o LLM
      """
    if not chunk_results:
        return ""

    return "\n".join([
        RAG_CHUNK_CONTEXT_TEMPLATE.format(
            chunk_number=i,
            document_title=chunk.document.title or "Documento sem título",
            document_source=chunk.document.source or "Fonte não disponível",
            chunk_content=chunk.content
        )
        for i, chunk in enumerate(chunk_results, 1)
    ])
