"""
Handler para gerar respostas diretas quando RAG deve ser pulado.

Fornece respostas empáticas e profissionais sem necessidade de buscar documentos,
mantendo a personalidade Mar.IA e a interface de streaming.
"""

from typing import TYPE_CHECKING, AsyncGenerator

from loguru import logger

from backend.constants import RAG_DIRECT_RESPONSE_PROMPT, RAG_SYSTEM_PROMPT
from backend.exceptions.http_exceptions import InternalServerException
from backend.integrations.llm import Message
from backend.modules.rag.rag_dto import RAGStreamChunk
from backend.modules.rag.rag_enum import RAGChunkKind

if TYPE_CHECKING:
    from backend.modules.rag.rag_service import RAGService


async def generate_direct_response(hub: "RAGService", user_input: str) -> AsyncGenerator[str, None]:
    """
    Gera resposta direta em streaming quando RAG deve ser pulado.

    Args:
        hub: Instância do RAGService com acesso ao LLM provider
        user_input: Mensagem/pergunta do usuário

    Yields:
        str: Chunks da resposta formatados para streaming SSE

    Raises:
        InternalServerException: Em caso de erro na geração da resposta
    """
    try:
        logger.info("Pulando RAG, gerando resposta direta ao LLM")

        # Prepara mensagem para o LLM adicionando contexto como prefixo da mensagem do usuário
        messages = [Message(
            role="user",
            content=RAG_DIRECT_RESPONSE_PROMPT.format(
                user_input=user_input
            )
        )]

        # Gera resposta em streaming com o system prompt padrão do Mar.IA
        async for chunk in hub.llm_provider.stream_chat(
            messages=messages,
            system_prompt=RAG_SYSTEM_PROMPT,
        ):
            if chunk.content:
                yield RAGStreamChunk(
                    content=chunk.content,
                    kind=RAGChunkKind.CONTENT
                ).streamed

        # Envia sinal de finalização
        yield RAGStreamChunk(kind=RAGChunkKind.FINAL).streamed

    except Exception as exception:
        raise InternalServerException(
            "Erro ao gerar resposta direta"
        ) from exception
