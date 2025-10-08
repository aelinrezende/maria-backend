"""
Gemini Provider - Implementação da interface LLM para Google Gemini.

Utiliza a SDK oficial google-genai para comunicação streaming
com os modelos Gemini.
"""

from typing import AsyncGenerator

from google import genai
from google.genai import types

from backend.interfaces.llm import ILLMConfig

from .exceptions import (
    GeminiError,
    LLMAuthenticationError,
)
from .models import Message, StreamChunk
from .protocol import ILLMProvider


class GeminiProvider(ILLMProvider):
    """
    Provider para comunicação com a API do Gemini.

    Implementa o protocolo ILLMProvider usando a SDK oficial
    google-genai para comunicação com a API do Gemini.
    """

    ROLE_MAP = {
        "user": "user",
        "assistant": "model",
    }

    @property
    def provider_name(self) -> str:
        """Nome do provedor."""
        return "gemini"

    def __init__(self, config: ILLMConfig) -> None:
        """
        Inicializa o provider do Gemini.

        Args:
            config: Configuração do Gemini (API key, modelo, etc.)
        """
        self.config = config

        try:
            self.client = genai.Client(api_key=config.api_key)

        except Exception as exception:
            raise LLMAuthenticationError(
                f"GEMINI_INITIALIZATION_ERROR: {exception}") from exception

    async def stream_chat(
        self,
        messages: list[Message],
        system_prompt: str | None = None
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Inicia chat streaming com Gemini.

        Args:
            messages: Lista de mensagens da conversa
            system_prompt: Prompt de sistema opcional

        Yields:
            StreamChunk: Chunks da resposta em streaming

        Raises:
            GeminiError: Em caso de erro na API do Gemini
        """
        contents = [
            types.ContentDict({
                "role": self.ROLE_MAP.get(message.role, "user"),
                "parts": [types.PartDict({"text": message.content})]
            }) for message in messages
        ]

        try:
            request_params = {
                "model": self.config.model,
                "contents": contents,
                "config": types.GenerateContentConfig(
                    max_output_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    system_instruction=system_prompt
                )
            }

            response = await self.client.aio.models.generate_content_stream(**request_params)

            async for chunk in response:
                if chunk.text:
                    yield StreamChunk(
                        content=chunk.text,
                        is_final=False
                    )

            yield StreamChunk(
                content="",
                is_final=True
            )

        except Exception as exception:
            raise GeminiError(f"GEMINI_API_ERROR: {exception}") from exception

    async def complete_message(
        self,
        message: str,
        system_prompt: str | None = None,
        temperature: float = 0.1
    ) -> str:
        """
        Completa uma única mensagem sem streaming.

        Args:
            message: Mensagem do usuário
            system_prompt: Prompt de sistema opcional
            temperature: Temperatura para controle de criatividade

        Returns:
            str: Resposta completa do LLM

        Raises:
            GeminiError: Em caso de erro na API do Gemini
        """
        try:
            # Prepara conteúdo da mensagem
            contents = [
                types.ContentDict({
                    "role": "user",
                    "parts": [types.PartDict({"text": message})]
                })
            ]

            # Prepara parâmetros da requisição
            request_params = {
                "model": self.config.model,
                "contents": contents,
                "config": types.GenerateContentConfig(
                    max_output_tokens=self.config.max_tokens,
                    temperature=temperature,
                    system_instruction=system_prompt
                )
            }

            # Faz requisição síncrona completa
            response = await self.client.aio.models.generate_content(**request_params)

            # Retorna conteúdo da resposta
            return response.text

        except Exception as exception:
            raise GeminiError(f"GEMINI_API_ERROR: {exception}") from exception
