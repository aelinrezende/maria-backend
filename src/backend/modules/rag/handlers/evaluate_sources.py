"""
Serviço para avaliação das fontes encontradas na busca semântica.

Avalia relevância dos chunks e determina se nova busca é necessária,
conforme Etapa 4 do pipeline RAG do Mar.IA.
"""

import json
from typing import TYPE_CHECKING, Awaitable, Callable, List, Tuple

from loguru import logger

from backend.constants.prompts import SOURCE_EVALUATION_PROMPT
from backend.core.config import settings
from backend.exceptions.http_exceptions import InternalServerException
from backend.models.chunk import Chunk
from backend.modules.rag.rag_dto import SourceEvaluationResult

if TYPE_CHECKING:
    from backend.modules.rag.rag_hub import RAGHub

ChunkEvaluationCallback = Callable[
    [List[str]], Awaitable[Tuple[List[Chunk], SourceEvaluationResult]]
]


async def evaluate_found_sources(
    hub: "RAGHub",
    user_query: str,
    chunks: List[str]
) -> SourceEvaluationResult:
    """
    Avalia se os chunks encontrados são suficientes e relevantes para responder à pergunta.

    Args:
        hub: Instância do RAGHub com acesso ao LLM
        user_query: Pergunta original do usuário
        chunks: Lista de chunks encontrados na busca semântica

    Returns:
        SourceEvaluationResult: Resultado da avaliação

    Raises:
        InternalServerException: Em caso de erro na avaliação ou parsing da resposta
    """
    if not settings.ENABLE_SOURCE_EVALUATION:
        logger.info(
            "Avaliação de fontes desabilitada, retornando resultado vazio padrão"
        )

        return SourceEvaluationResult.empty()

    if not chunks:
        logger.info(
            "Nenhum chunk encontrado para avaliação de fontes, retornando vazio"
        )

        return SourceEvaluationResult.empty()

    try:
        # Formata chunks para o prompt
        formatted_chunks = [
            f"---\nChunk {i}: {chunk}" for i, chunk in enumerate(chunks) if chunk.strip()
        ]

        # Formata prompt com entrada do usuário e chunks
        evaluation_prompt = SOURCE_EVALUATION_PROMPT.format(
            user_query=user_query,
            chunks="\n".join(formatted_chunks)
        )

        # Solicita avaliação ao LLM com baixa temperatura para maior previsibilidade
        response = await hub.llm_provider.complete_message(
            message=evaluation_prompt,
            temperature=0.1,
            as_json=True
        )

        # Tenta fazer parsing da resposta JSON usando o utilitário
        try:
            return SourceEvaluationResult(**json.loads(response))

        except (KeyError, TypeError, ValueError) as exception:
            logger.warning(
                f"Falha ao fazer parsing da resposta JSON (SourceEvaluationResult): {exception}; {response}"
            )

            return SourceEvaluationResult.empty()

    except Exception as exception:
        raise InternalServerException(
            "Erro ao avaliar relevância das fontes encontradas"
        ) from exception


async def rag_chunk_evaluation(
    hub: "RAGHub",
    query: str,
    callback: Callable[[List[str]], Awaitable[List[Chunk]]],
) -> List[Chunk]:
    """
    Realiza a lógica de tentativas múltiplas para busca e avaliação de chunks.

    Args:
        hub: Instância do RAGHub com acesso ao LLM
        query: Pergunta original do usuário
        callback: Função assíncrona que recebe IDs de chunks irrelevantes e retorna
        uma lista de chunks similares encontrados, excluindo os irrelevantes.
    Returns:
        Lista de chunks avaliados como relevantes
    """
    # Se avaliação de fontes estiver desabilitada, faz busca direta
    if not settings.ENABLE_SOURCE_EVALUATION:
        logger.info("Avaliação de fontes desabilitada - usando busca direta")

        return await callback([])

    # Fluxo normal com avaliação de fontes habilitada
    logger.info(
        "Avaliação de fontes habilitada - usando lógica de tentativas múltiplas")

    search_attempt = 0
    similar_chunks = []
    excluded_chunk_ids: List[str] = []

    while search_attempt < settings.RAG_MAX_SEARCH_ATTEMPTS:
        logger.info(
            f"Tentativa de busca RAG {search_attempt + 1}/{settings.RAG_MAX_SEARCH_ATTEMPTS}"
        )

        search_attempt += 1
        chunks: List[Chunk] = await callback(excluded_chunk_ids)

        # Avalia os chunks encontrados
        evaluation = await evaluate_found_sources(hub, query, [
            chunk.content for chunk in chunks
        ])

        if not chunks:
            return []

        irrelevant = evaluation.irrelevant_chunks_zero_based_indexes

        # Filtrar chunks irrelevantes
        similar_chunks.extend([
            chunk for i, chunk in enumerate(chunks)
            if i not in irrelevant
        ])

        excluded_chunk_ids.extend([chunk.id for chunk in chunks])

        if not evaluation.requires_new_query:
            break

    logger.debug(f"Chunks similares encontrados: {len(similar_chunks)}")

    return similar_chunks
