"""
Protocol para integração LLM.

Define a interface comum que todos os provedores LLM devem implementar.
Foca apenas em streaming para simplicidade e performance.
"""

from typing import AsyncGenerator, Protocol

from backend.interfaces.llm import ILLMConfig

from .models import Message, StreamChunk


class ILLMProvider(Protocol):
    """
    Protocol que define a interface comum para todos os provedores LLM.

    Todos os provedores devem implementar este protocolo para garantir
    compatibilidade e intercambialidade.
    """

    def __init__(self, config: ILLMConfig) -> None:
        """
        Inicializa o provedor com configuração.

        Args:
            config: Configuração específica do provedor
        """

    async def stream_chat(
        self,
        messages: list[Message],
        system_prompt: str | None = None
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Inicia chat streaming com o LLM.

        Args:
            messages: Lista de mensagens da conversa
            system_prompt: Prompt de sistema opcional

        Yields:
            StreamChunk: Chunks da resposta em streaming

        Raises:
            LLMError: Em caso de erro na comunicação
        """
        yield StreamChunk(...)

    async def complete_message(
        self,
        message: str,
        system_prompt: str | None = None,
        temperature: float = 0.1
    ) -> str:
        """
        Completa uma única mensagem sem streaming.

        Usa baixa temperatura para resposta mais previsível.
        Ideal para avaliações e classificações.

        Args:
            message: Mensagem do usuário
            system_prompt: Prompt de sistema opcional
            temperature: Temperatura para controle de criatividade (padrão: 0.1)

        Returns:
            str: Resposta completa do LLM

        Raises:
            LLMError: Em caso de erro na comunicação
        """

    @property
    def provider_name(self) -> str:
        """
        Nome do provedor para identificação.

        Returns:
            str: Nome do provedor (ex: "claude", "gemini")
        """
