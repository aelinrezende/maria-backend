"""Repositório para operações de persistência de Message."""


from typing import List, Optional

from fastapi.params import Depends
from sqlmodel import col, desc
from wireup import service

from backend.core.database import DatabaseConnection
from backend.models.chunk import Chunk
from backend.models.message import Message
from backend.modules.base.base_dto import PaginatedResponse, PaginateRequest
from backend.modules.base.base_repository import BaseRepository
from backend.modules.message.message_dto import ConversationPair, MessageResponse
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
            user_id=user_id,
            content=user_input,
            author_role=MessageRole.USER
        )

        assistant_message = Message(
            user_id=user_id,
            content=assistant_response,
            author_role=MessageRole.ASSISTANT,
            chunks=similar_chunks or []
        )

        self.insert_multiple([user_message, assistant_message])

        return ConversationPair(user_message, assistant_message)

    async def get_last_n_messages(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Message]:
        """
        Recupera as últimas N mensagens de um usuário, ordenadas por data (mais antigas primeiro).

        Args:
            user_id: ID do usuário
            limit: Número máximo de mensagens a recuperar

        Returns:
            Lista de mensagens ordenadas por created_at (mais antigas primeiro)
        """
        query = self.query.where(
            col(Message.user_id) == user_id,
            col(Message.author_role).in_(  # pylint: disable=E1101
                [MessageRole.USER, MessageRole.ASSISTANT]
            )).order_by(desc(Message.created_at)).limit(limit)

        result = await self.run(query)

        return list(reversed(result.scalars().all()))

    async def get_cursor_paginated_messages(
        self,
        user_id: str,
        request: PaginateRequest,
    ) -> PaginatedResponse[MessageResponse]:
        """
        Recupera mensagens paginadas usando cursor-based pagination.

        Args:
            user_id: ID do usuário
            limit: Número máximo de mensagens a retornar
            cursor: Timestamp do cursor para paginação (None para primeira página)

        Returns:
            PaginatedResponse com MessageResponse formatados e metadados de paginação
        """
        query = self.query.where(
            col(Message.user_id) == user_id
        )
        print("request:", request)
        cursor, limit = request.cursor, request.limit

        if cursor:
            query = query.where(col(Message.created_at) < cursor)

        # Ordena por data descendente (mais recentes primeiro)
        query = query.order_by(desc(Message.created_at)).limit(limit + 1)
        messages = list((await self.run(query)).scalars().all())

        has_next = len(messages) > limit

        # Remove a mensagem extra usada para verificação
        if has_next:
            messages = messages[:limit]

        # Reverte para ordem cronológica (mais antigas primeiro)
        messages = list(reversed(messages))

        cursor_next = None

        if has_next and messages:
            # Usa a created_at da última mensagem retornada como próximo cursor
            cursor_next = messages[-1].created_at

        return PaginatedResponse[MessageResponse](
            data=MessageResponse.from_messages(messages),
            has_next=has_next,
            cursor_next=cursor_next
        )
