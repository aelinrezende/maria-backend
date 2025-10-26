
from typing import TYPE_CHECKING, AsyncGenerator, List

from loguru import logger
from sqlalchemy.orm import selectinload
from sqlmodel import col

from backend.constants.prompts import (
    RAG_NO_SOURCES_PROMPT_TEMPLATE,
    RAG_SYSTEM_PROMPT,
    RAG_USER_PROMPT_TEMPLATE,
)
from backend.integrations.llm.models import Message
from backend.models.chunk import Chunk
from backend.modules.rag import handlers
from backend.modules.rag.handlers.source_extraction import extract_source_info
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
    1. Expande e extrai entidades da query (se habilitado).
    2. Gera embedding da query expandida.
    3. Busca chunks similares no banco.
    4. Prepara prompt baseado na disponibilidade de chunks.
        1. Refina e reordena os chunks encontrados via LLM (se habilitado).
        2. Informa a ausência de contexto.
    5. Gera resposta com LLM em streaming.
    """
    logger.info(f"Iniciando orquestração RAG para query: {query}")

    # 1. Expansão e extração da query
    expansion_result = await handlers.expand_user_query(hub, query)
    entities_and_keywords = "\n".join(expansion_result.entities_and_keywords)
    expanded_query = expansion_result.improved_input

    # 2. Gerar embedding da query expandida
    query_embedding, *_ = await hub.embeddings.embed_queries([entities_and_keywords])

    # 3. Busca chunks similares com avaliação de fontes
    similar_chunks = await handlers.rag_chunk_evaluation(
        hub,
        expanded_query,
        _search_similar_chunks(hub, query_embedding)
    )

    # 4. Prepara prompt baseado na disponibilidade de chunks
    if similar_chunks:
        # 4.1 Refinamento e estruturação dos chunks encontrados
        refinement_result = await handlers.refine_and_reorder_chunks(hub, similar_chunks, expanded_query)

        # Usa o texto refinado no prompt do usuário
        user_prompt = RAG_USER_PROMPT_TEMPLATE.format(
            chunks_context=refinement_result.refined_text,
            user_query=expanded_query
        )
    else:
        # 4.2 Usa prompt especializado para ausência de fontes
        user_prompt = RAG_NO_SOURCES_PROMPT_TEMPLATE.format(
            user_query=expanded_query
        )

    # Extrai informações estruturadas das fontes
    sources = extract_source_info(similar_chunks)

    yield RAGStreamChunk(
        kind=RAGChunkKind.SOURCES,
        sources=sources
    ).streamed

    # 5. Gera resposta com LLM em streaming
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


def _search_similar_chunks(
    hub: "RAGService",
    query_embedding: List[float]
):
    """
    Retorna uma função de callback para buscar chunks similares, excluindo chunks já utilizados.
    Args:
        query_embedding: Embedding da query do usuário
    Returns:
        Função assíncrona para buscar chunks similares
    """
    async def callback(excluded_chunk_ids: List[str]) -> List[Chunk]:
        return await hub.chunk_repository.get_similar(
            query_embedding,
            builder=lambda query: query.where(col(Chunk.id).not_in(excluded_chunk_ids)).options(
                selectinload(Chunk.document)
            ),
        )

    return callback
