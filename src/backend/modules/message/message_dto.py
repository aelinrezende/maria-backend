"""DTOs para mensagens."""

from typing import NamedTuple

from backend.models.message import Message


class ConversationPair(NamedTuple):
    """Tupla para armazenar mensagens do usuário e do assistente."""
    user_message: Message
    assistant_message: Message
