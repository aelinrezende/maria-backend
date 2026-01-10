"""Serviço para gerenciamento de mensagens."""


from fastapi.params import Depends
from wireup import service

from backend.core.unit_of_work import UnitOfWork
from backend.modules.auth import handlers


@service(lifetime="scoped")
class AuthHub:
    """Serviço para operações de negócio com mensagens."""

    def __init__(self, unit_of_work: UnitOfWork = Depends()):
        self.unit_of_work = unit_of_work
        self.handlers = handlers
