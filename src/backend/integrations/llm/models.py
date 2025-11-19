"""
Modelos de dados para integração LLM.

Define estruturas de dados tipadas para mensagens, chunks de streaming
e configurações dos provedores LLM.
"""

from dataclasses import dataclass
from typing import List, Literal

from backend.core.config import settings
from backend.interfaces.llm import ILLMConfig
from backend.models.message import Message as MessageModel


@dataclass
class Message:
    """Representa uma mensagem no chat."""
    role: Literal["user", "assistant"]
    content: str

    @staticmethod
    def from_messages_model(messages: List[MessageModel]) -> List["Message"]:
        """
        Converte um modelo de mensagem do banco para o modelo Message.

        Args:
            message: Instância do modelo de mensagem do banco
        """
        return [Message(
            role=message.author_role.value.lower(),
            content=message.content
        ) for message in messages]


@dataclass
class StreamChunk:
    """Representa um chunk de resposta streaming."""
    content: str
    is_final: bool = False


@dataclass
class ClaudeConfig(ILLMConfig):
    """Configuração específica para o provedor Claude."""
    api_key: str = settings.CLAUDE_API_KEY
    model: str = settings.CLAUDE_MODEL
    max_tokens: int = settings.CLAUDE_MAX_TOKENS
    temperature: float = settings.CLAUDE_TEMPERATURE


@dataclass
class GeminiConfig(ILLMConfig):
    """Configuração específica para o provedor Gemini."""
    api_key: str = settings.GEMINI_API_KEY
    model: str = settings.GEMINI_MODEL
    max_tokens: int = settings.GEMINI_MAX_TOKENS
    temperature: float = settings.GEMINI_TEMPERATURE


@dataclass
class GLMConfig(ILLMConfig):
    """Configuração específica para o provedor GLM da Z.AI."""
    api_key: str = settings.ZAI_API_KEY
    model: str = settings.ZAI_MODEL
    max_tokens: int = settings.ZAI_MAX_TOKENS
    temperature: float = settings.ZAI_TEMPERATURE
