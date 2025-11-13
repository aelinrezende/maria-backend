"""
GLM Provider - Implementação da interface LLM para GLM da Z.AI.

Utiliza o cliente OpenAI SDK para comunicação streaming com os modelos GLM
através da API da Z.AI.
"""

from typing import AsyncGenerator

import openai

from backend.core.config import settings
from backend.interfaces.llm import ILLMConfig

from .exceptions import (
    GLMError,
    LLMAuthenticationError,
    LLMConnectionError,
    LLMRateLimitError,
)
from .models import Message, StreamChunk
from .protocol import ILLMProvider


class GLMProvider(ILLMProvider):
    """
    Provider para comunicação com a API do GLM da Z.AI.

    Implementa o protocolo ILLMProvider usando o cliente OpenAI SDK
    configurado para usar o endpoint da Z.AI.
    """

    @property
    def provider_name(self) -> str:
        """Nome do provedor."""
        return "glm"

    def __init__(self, config: ILLMConfig) -> None:
        """
        Inicializa o provider do GLM.

        Args:
            config: Configuração do GLM (API key, base URL, modelo, etc.)
        """
        self.config = config

        try:
            self.client = openai.AsyncOpenAI(
                api_key=config.api_key,
                base_url=settings.ZAI_BASE_URL,
            )
        except Exception as exception:
            raise LLMAuthenticationError(
                f"ZAI_INITIALIZATION_ERROR: {exception}"
            ) from exception

    async def stream_chat(
        self,
        messages: list[Message],
        system_prompt: str | None = None
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Inicia chat streaming com GLM.

        Args:
            messages: Lista de mensagens da conversa
            system_prompt: Prompt de sistema opcional

        Yields:
            StreamChunk: Chunks da resposta em streaming

        Raises:
            GLMError: Em caso de erro na API do GLM
        """
        try:
            conversation = [
                {"role": message.role, "content": message.content}
                for message in messages
            ]

            params = {
                "model": self.config.model,
                "messages": conversation,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "stream": True
            }

            if system_prompt:
                params["messages"].insert(
                    0, {"role": "system", "content": system_prompt}
                )

            stream = await self.client.chat.completions.create(**params)

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield StreamChunk(
                        content=chunk.choices[0].delta.content,
                        is_final=False
                    )

            yield StreamChunk(content="", is_final=True)

        except openai.AuthenticationError as exception:
            raise LLMAuthenticationError(
                f"ZAI_AUTHENTICATION_ERROR: {exception}"
            ) from exception

        except openai.RateLimitError as exception:
            raise LLMRateLimitError(
                f"ZAI_RATE_LIMIT_EXCEEDED: {exception}"
            ) from exception

        except openai.APIConnectionError as exception:
            raise LLMConnectionError(
                f"ZAI_CONNECTION_ERROR: {exception}"
            ) from exception

        except Exception as exception:
            raise GLMError(
                f"ZAI_UNEXPECTED_ERROR: {exception}"
            ) from exception

    async def complete_message(
        self,
        message: str,
        system_prompt: str | None = None,
        temperature: float = 0.1,
        as_json: bool = False
    ) -> str:
        """
        Completa uma única mensagem sem streaming.

        Args:
            message: Mensagem do usuário
            system_prompt: Prompt de sistema opcional
            temperature: Temperatura para controle de criatividade
            as_json: Se deve retornar a resposta como JSON

        Returns:
            str: Resposta completa do LLM

        Raises:
            GLMError: Em caso de erro na API do GLM
        """
        try:
            messages = [{"role": "user", "content": message}]

            if system_prompt:
                messages.insert(
                    0, {"role": "system", "content": system_prompt}
                )

            params = {
                "model": self.config.model,
                "messages": messages,
                "max_tokens": self.config.max_tokens,
                "temperature": temperature
            }

            if as_json:
                params["response_format"] = {"type": "json_object"}

            response = await self.client.chat.completions.create(**params)
            choices = response.choices

            if choices and choices[0].message.content:
                return choices[0].message.content

            return ""

        except openai.AuthenticationError as exception:
            raise LLMAuthenticationError(
                f"ZAI_AUTHENTICATION_ERROR: {exception}"
            ) from exception

        except openai.RateLimitError as exception:
            raise LLMRateLimitError(
                f"ZAI_RATE_LIMIT_EXCEEDED: {exception}"
            ) from exception

        except openai.APIConnectionError as exception:
            raise LLMConnectionError(
                f"ZAI_CONNECTION_ERROR: {exception}"
            ) from exception

        except Exception as exception:
            raise GLMError(
                f"ZAI_UNEXPECTED_ERROR: {exception}"
            ) from exception
