"""Handler para refinamento e reordenação de chunks RAG."""

from ast import List
from typing import TYPE_CHECKING

from loguru import logger

from backend.constants.prompts import (
    CHUNK_REFINEMENT_PROMPT,
    RAG_CHUNK_CONTEXT_TEMPLATE,
    RAG_SYSTEM_PROMPT,
)
from backend.core.config import settings
from backend.models.chunk import Chunk
from backend.modules.rag.rag_dto import ChunkRefinementResponse

if TYPE_CHECKING:
    from backend.modules.rag.rag_service import RAGService


async def refine_and_reorder_chunks(
    hub: "RAGService",
    chunks: List[Chunk],
    query: str
) -> ChunkRefinementResponse:
    """
    Refina e reordena os chunks encontrados usando LLM para agrupamento semântico.

    Args:
        hub: Instância do RAGService com acesso ao LLM provider
        chunks: Lista de chunks encontrados na busca
        query: Consulta original do usuário

    Returns:
        ChunkRefinementResponse: Com o texto refinado e reestruturado
    """

    # Verifica se o refinamento está habilitado
    if not settings.ENABLE_CHUNK_REFINEMENT:
        logger.info("Refinamento de chunks desabilitado, usando texto original")

        # Prepara fallback concatenando o conteúdo original dos chunks
        return ChunkRefinementResponse.fallback(chunks)

    try:
        logger.info(f"Iniciando refinamento de {len(chunks)} chunks")

        # Prepara o texto dos chunks para o prompt
        chunks_text = _format_chunks_context(chunks)

        # Prepara o prompt com a consulta e chunks do usuário
        prompt = CHUNK_REFINEMENT_PROMPT.format(
            user_query=query,
            chunks=chunks_text
        )

        # Chama o LLM para refinamento com temperatura 0.2 (para consistência e preservação)
        response_content = await hub.llm_provider.complete_message(
            message=prompt,
            system_prompt=RAG_SYSTEM_PROMPT,
            temperature=0.2
        )

        # Processa resposta como texto simples (sem parsing JSON)
        refined_text = response_content.strip()

        # Valida que o conteúdo não está vazio
        if not refined_text:
            logger.warning(
                "Resposta do refinamento está vazia, usando fallback"
            )

            return ChunkRefinementResponse.fallback(chunks)

        logger.info(
            f"Refinamento concluído com sucesso. "
            f"Texto original: {len(chunks)} chunks, "
            f"texto refinado: {len(refined_text)} caracteres"
        )

        return ChunkRefinementResponse(refined_text=refined_text)

    except Exception as exception:
        logger.error(
            f"Erro ao fazer refinamento de chunks: {exception}\n"
            "Usando fallback para texto original"
        )

        # Prepara fallback concatenando o conteúdo original dos chunks
        return ChunkRefinementResponse.fallback(chunks)


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
