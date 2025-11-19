"""Middleware para carregar contexto histórico de mensagens."""

from contextvars import ContextVar
from typing import List, Optional

from fastapi.params import Depends

from backend.core.config import settings
from backend.cross_cutting.middleware.auth.auth import get_requesting_user
from backend.integrations.llm import Message as LLMMessage
from backend.models.message import Message
from backend.modules.message.message_repository import MessageRepository

conversation_history: ContextVar[
    List[Message]
] = ContextVar('conversation_history', default=[])


def set_chat_messages(messages: List[Message]) -> None:
    """
    Define o histórico de conversas para o contexto atual.

    Args:
        messages: Lista de mensagens do usuário
    """
    conversation_history.set(messages)


def get_chat_messages() -> Optional[List[Message]]:
    """
    Retorna o histórico de conversas do contexto atual.

    Returns:
        Lista de mensagens ou None se não definido
    """
    return conversation_history.get()


def get_chat_context() -> Optional[List[LLMMessage]]:
    """
    Retorna N últimas mensagens do histórico no formato LLMMessage.

    Returns:
        Lista de mensagens ou None se não definido
    """
    return LLMMessage.from_messages_model(conversation_history.get())


async def load_user_messages(
    message_repository: MessageRepository = Depends()
) -> List["Message"]:
    """
    Retorna o histórico de conversas contendo as N últimas mensagens.

    Returns:
        Lista de mensagens no formato Message
    """
    requesting_user = get_requesting_user()

    messages = await message_repository.get_last_n_messages(
        requesting_user.id, settings.RAG_MAX_CONTEXT_MESSAGES
    )

    set_chat_messages(messages)

    return messages
