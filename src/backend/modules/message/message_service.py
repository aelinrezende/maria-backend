"""Serviço para gerenciamento de mensagens."""


from fastapi.params import Depends
from wireup import service

from backend.core.unit_of_work import UnitOfWork
from backend.models.message import Message
from backend.modules.base.base_service import BaseService
from backend.modules.message.message_repository import MessageRepository


@service(lifetime="scoped")
class MessageService(BaseService[Message]):
    """Serviço para operações de negócio com mensagens."""

    def __init__(self, repository: MessageRepository = Depends(), unit_of_work: UnitOfWork = Depends()):
        super().__init__(repository, Message, unit_of_work)
        self.repository = repository
