"""Serviço para gerenciamento de mensagens."""


from fastapi.params import Depends
from wireup import service

from backend.core.unit_of_work import UnitOfWork
from backend.models.message import Message
from backend.modules.base.base_hub import BaseHub
from backend.modules.message import handlers
from backend.modules.message.message_repository import MessageRepository


@service(lifetime="scoped")
class MessageHub(BaseHub[Message]):
    """Serviço para operações de negócio com mensagens."""

    def __init__(self, repository: MessageRepository = Depends(), unit_of_work: UnitOfWork = Depends()):
        super().__init__(repository, Message, unit_of_work)
        self.repository = repository
        self.handlers = handlers
