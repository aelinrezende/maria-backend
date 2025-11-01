from fastapi.params import Depends
from wireup import service

from backend.core.unit_of_work import UnitOfWork
from backend.models.session import Session
from backend.modules.base.base_service import BaseService
from backend.modules.session.session_repository import SessionRepository


@service(lifetime="scoped")
class SessionService(BaseService[Session]):
    """
    Serviço para operações relacionadas a sessões.
    """

    def __init__(
        self,
        repository: SessionRepository = Depends(),
        unit_of_work: UnitOfWork = Depends()
    ):
        super().__init__(repository, Session, unit_of_work)
