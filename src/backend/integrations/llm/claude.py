"""
Claude Provider - Implementação da interface LLM para Anthropic Claude.

Utiliza o cliente oficial da Anthropic para comunicação streaming
com os modelos Claude.
"""

from typing import AsyncGenerator

import anthropic

from backend.interfaces.llm import ILLMConfig

from .exceptions import (
    ClaudeError,
    LLMAuthenticationError,
    LLMConnectionError,
    LLMRateLimitError,
)
from .models import Message, StreamChunk
from .protocol import ILLMProvider


class ClaudeProvider(ILLMProvider):
    """
    Provider para comunicação com a API do Claude.

    Implementa o protocolo ILLMProvider usando o cliente oficial
    da Anthropic com suporte a streaming.
    """

    def __init__(self, config: ILLMConfig) -> None:
        """
        Inicializa o provider do Claude.

        Args:
            config: Configuração do Claude (API key, modelo, etc.)
        """
        self.config = config

        try:
            self.client = anthropic.AsyncAnthropic(
                api_key=config.api_key,
                http_client=anthropic.DefaultAioHttpClient()
            )
        except Exception as exception:
            raise LLMAuthenticationError(
                f"CLAUDE_INITIALIZATION_ERROR: {exception}") from exception

    async def stream_chat(
        self,
        messages: list[Message],
        system_prompt: str | None = None
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Inicia chat streaming com Claude.

        Args:
            messages: Lista de mensagens da conversa
            system_prompt: Prompt de sistema opcional

        Yields:
            StreamChunk: Chunks da resposta em streaming

        Raises:
            ClaudeError: Em caso de erro na API do Claude
        """
        try:
            # Converte mensagens para formato do Claude
            parsed_messages = [
                {"role": message.role, "content": message.content}
                for message in messages
                if message.role != "system"
            ]

            # Prepara parâmetros da requisição
            request_params = {
                "model": self.config.model,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "messages": parsed_messages,
            }

            # Adiciona system prompt se fornecido
            if system_prompt:
                request_params["system"] = system_prompt

            # Inicia streaming
            async with self.client.messages.stream(**request_params) as stream:
                async for chunk in stream.text_stream:
                    yield StreamChunk(
                        content=chunk,
                        is_final=False
                    )

                # Envia chunk final para indicar fim do streaming
                yield StreamChunk(
                    content="",
                    is_final=True
                )

        except anthropic.AuthenticationError as exception:
            raise LLMAuthenticationError(
                f"CLAUDE_AUTHENTICATION_ERROR: {exception}") from exception

        except anthropic.RateLimitError as exception:
            raise LLMRateLimitError(
                f"CLAUDE_RATE_LIMIT_EXCEEDED: {exception}") from exception

        except anthropic.APIConnectionError as exception:
            raise LLMConnectionError(
                f"CLAUDE_CONNECTION_ERROR: {exception}") from exception

        except Exception as exception:
            raise ClaudeError(
                f"CLAUDE_UNEXPECTED_ERROR: {exception}") from exception

    @property
    def provider_name(self) -> str:
        """Nome do provedor."""
        return "claude"
