"""
Serviço para avaliação da entrada do usuário.

Determina se uma pergunta precisa de busca RAG ou pode ser respondida diretamente,
otimizando performance e direcionando casos emergenciais adequadamente.
"""

import json
from typing import TYPE_CHECKING

from loguru import logger

from backend.constants.prompts import USER_INPUT_EVALUATION_PROMPT
from backend.core.config import settings
from backend.exceptions.http_exceptions import InternalServerException
from backend.modules.rag.rag_dto import UserInputEvaluation

if TYPE_CHECKING:
    from backend.modules.rag.rag_service import RAGService


async def should_skip_rag(hub: "RAGService", user_input: str) -> bool:
    """
      Avalia se deve pular a busca RAG para a entrada do usuário.

      Args:
          user_input: Mensagem/pergunta do usuário

      Returns:
          bool: True se deve pular RAG, False se deve usar RAG

      Raises:
          Exception: Em caso de erro na avaliação ou parsing da resposta
      """
    # Se avaliação está desabilitada, sempre usa RAG completo
    if not settings.ENABLE_USER_INPUT_EVALUATION:
        logger.info(
            "Avaliação de entrada do usuário desabilitada, usando fluxo RAG completo"
        )

        return False

    try:
        # Formata prompt com entrada do usuário
        evaluation_prompt = USER_INPUT_EVALUATION_PROMPT.format(
            user_input=user_input
        )

        # Solicita avaliação ao LLM com baixa temperatura para maior previsibilidade
        response = await hub.llm_provider.complete_message(
            message=evaluation_prompt,
            temperature=0.1,
            as_json=True
        )

        # Faz parsing da resposta JSON
        evaluation = UserInputEvaluation(**json.loads(response.strip()))

        return evaluation.skip

    except Exception as exception:
        raise InternalServerException(
            "Erro ao avaliar necessidade de RAG"
        ) from exception
