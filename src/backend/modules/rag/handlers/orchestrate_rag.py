
from typing import TYPE_CHECKING, AsyncGenerator, List, Tuple

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
from backend.modules.rag.rag_dto import (
    QueryExpansionResponse,
    RAGStreamChunk,
    SourceEvaluationResult,
)
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
        1. Refinamento e estruturação dos chunks encontrados.
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

    # 3. Busca chunks similares com lógica de tentativas múltiplas
    similar_chunks = await handlers.rag_chunk_evaluation(_search_and_evaluate_sources(
        hub,
        query_embedding,
        expansion_result
    ))

    # 4. Prepara prompt baseado na disponibilidade de chunks
    if similar_chunks:
        # 4.1 TODO: Refinamento e estruturação dos chunks encontrados
        user_prompt = RAG_USER_PROMPT_TEMPLATE.format(
            chunks_context=_format_chunks_context(similar_chunks),
            user_query=expanded_query
        )
    else:
        # 4.2 TODO: Informa a ausência de contexto
        user_prompt = (
            f"Entrada do usuário: {query}\n\n"
            f"Não foram encontrados documentos relevantes sobre este tópico."
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


def _search_and_evaluate_sources(
        hub: "RAGService",
        query_embedding: List[float],
        expansion: QueryExpansionResponse,
):
    """
    Retorna uma função de callback para busca e avaliação de fontes com exclusão de chunks irrelevantes.
    Args:
        hub: Instância do RAGService com acesso ao repositório de chunks e LLM
        query_embedding: Embedding da query expandida
        expansion: Resultado da expansão da query
    Returns:
        Função de callback que realiza a busca e avaliação de fontes
    """
    async def callback(excluded_chunk_ids: List[int]) -> Tuple[List[Chunk], SourceEvaluationResult]:
        chunks: List[Chunk] = await hub.chunk_repository.get_similar(
            query_embedding,
            builder=lambda query: query.where(col(Chunk.id).not_in(excluded_chunk_ids)).options(
                selectinload(Chunk.document)
            ),
        )

        evaluation = await handlers.evaluate_found_sources(hub, expansion.improved_input, [
            chunk.content for chunk in chunks
        ])

        return (chunks, evaluation)

    return callback
