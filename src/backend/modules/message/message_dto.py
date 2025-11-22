"""DTOs para mensagens."""

from datetime import datetime
from typing import List, NamedTuple

from backend.models.base import BaseModel
from backend.models.message import Message


class ConversationPair(NamedTuple):
    """Tupla para armazenar mensagens do usuário e do assistente."""
    user_message: Message
    assistant_message: Message


class MessageResponse(BaseModel):
    """Resposta de mensagem individual."""
    id: str
    content: str
    author_role: str
    created_at: datetime

    @staticmethod
    def from_messages(messages: List[Message]) -> List["MessageResponse"]:
        """Cria uma lista de MessageResponse a partir de uma lista de Message."""
        return [MessageResponse(
            id=message.id,
            content=message.content,
            author_role=message.author_role.value,
            created_at=message.created_at
        ) for message in messages]
