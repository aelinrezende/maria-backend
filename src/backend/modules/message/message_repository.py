"""Repositório para operações de persistência de Message."""


from typing import List, Optional

from fastapi.params import Depends
from wireup import service

from backend.core.database import DatabaseConnection
from backend.models.chunk import Chunk
from backend.models.message import Message
from backend.modules.base.base_repository import BaseRepository
from backend.modules.message.message_dto import ConversationPair
from backend.modules.message.message_enums import MessageRole


@service(lifetime="scoped")
class MessageRepository(BaseRepository[Message]):
    """Repositório para operações de banco com Message."""

    def __init__(self, connection: DatabaseConnection = Depends()):
        super().__init__(Message, connection)

    def insert_conversation(
        self,
        user_id: str,
        user_input: str,
        assistant_response: str,
        similar_chunks: Optional[List[Chunk]] = None
    ) -> ConversationPair:
        """
        Insere uma conversa composta por mensagem do usuário e do assistente.

        :param user_id: ID do usuário.
        :param user_input: Mensagem enviada pelo usuário.
        :param assistant_response: Resposta gerada pelo assistente.
        :param similar_chunks: Lista opcional de trechos similares (chunks) associados à resposta do assistente.
        :return: Tupla com as mensagens inseridas (usuário, assistente).
        """
        user_message = Message(
            user_id=user_id, content=user_input, author_role=MessageRole.USER
        )

        assistant_message = Message(
            content=assistant_response,
            author_role=MessageRole.ASSISTANT,
            chunks=similar_chunks or []
        )

        self.insert_multiple([user_message, assistant_message])

        return ConversationPair(user_message, assistant_message)
