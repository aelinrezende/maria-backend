"""DTOs para mensagens."""


from typing import List, NamedTuple, Optional

from pydantic import Field

from backend.models.message import Message
from backend.modules.base.base_dto import BaseResponse, ModelBase
from backend.modules.document.document_enums import DocumentKind


class ConversationPair(NamedTuple):
    """Tupla para armazenar mensagens do usuário e do assistente."""
    user_message: Message
    assistant_message: Message


class SourceInfo(BaseResponse):
    """Informações estruturadas de uma fonte utilizada no RAG."""
    id: str = Field()
    order: int = Field()
    title: str = Field()
    source: str = Field()
    authors: List[str] = Field(default_factory=list)
    summary: str = Field()
    kind: DocumentKind = Field()
    url: Optional[str] = Field(default=None)
    date: Optional[str] = Field(default=None)


class MessageResponse(ModelBase):
    """Resposta de mensagem individual."""
    id: str
    content: str
    author_role: str
    sources: List[SourceInfo] = []

    @staticmethod
    def from_messages(messages: List[Message]) -> List["MessageResponse"]:
        """Cria uma lista de MessageResponse a partir de uma lista de Message."""

        messages = [MessageResponse(
            **message.model_dump(),
            sources=[
                SourceInfo(
                    **chunk.document.model_dump(),
                    order=index,
                    date=chunk.document.meta.get("date")
                )
                for index, chunk in enumerate(message.chunks, 1)
            ]
        ) for message in messages]

        for message in messages:
            message.sources = list({
                source.id: source for source in reversed(
                    message.sources
                )
            }.values())

        return messages


MessageResponse.model_rebuild()
