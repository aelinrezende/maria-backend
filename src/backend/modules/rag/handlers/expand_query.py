"""Handler para expansão e extração de consultas RAG."""

import json
from typing import TYPE_CHECKING

from loguru import logger

from backend.constants.prompts import QUERY_EXPANSION_PROMPT, RAG_SYSTEM_PROMPT
from backend.core.config import settings
from backend.exceptions.http_exceptions import InternalServerException
from backend.modules.rag.rag_dto import QueryExpansionResponse

if TYPE_CHECKING:
    from backend.modules.rag.rag_hub import RAGHub


async def expand_user_query(hub: "RAGHub", query: str) -> QueryExpansionResponse:
    """
    Expande e extrai entidades da consulta do usuário para melhorar a precisão da busca.

    Args:
        hub: Instância do RAGHub com acesso ao LLM provider
        query: Consulta original do usuário

    Returns:
        QueryExpansionResponse: Com a query expandida e entidades extraídas
    """

    # Verifica se a expansão está habilitada
    if not settings.ENABLE_QUERY_EXPANSION:
        logger.info("Expansão de consultas desabilitada, usando query original")

        return QueryExpansionResponse.fallback(query)

    try:
        # Prepara o prompt com a consulta do usuário
        prompt = QUERY_EXPANSION_PROMPT.format(user_input=query)

        # Chama o LLM para expansão usando complete_message para resposta completa
        response_content = await hub.llm_provider.complete_message(
            message=prompt,
            system_prompt=RAG_SYSTEM_PROMPT,
            as_json=True
        )

        return QueryExpansionResponse(**json.loads(response_content.strip()))

    except (json.JSONDecodeError, TypeError) as exception:
        logger.error(
            f"""Erro ao fazer parsing da resposta de expansão: \n{exception}\nUsando fallback para query original"""
        )

        return QueryExpansionResponse.fallback(query)

    except Exception as exception:
        raise InternalServerException(
            "Erro ao expandir consulta"
        ) from exception
