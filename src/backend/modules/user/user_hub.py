

from fastapi.params import Depends
from wireup import service

from backend.core.unit_of_work import UnitOfWork
from backend.integrations.mailgun import MailGun
from backend.models.user import User
from backend.modules.base.base_hub import BaseHub
from backend.modules.session.session_repository import SessionRepository
from backend.modules.user import handlers
from backend.modules.user.user_repository import UserRepository


@service(lifetime="scoped")
class UserHub(BaseHub[User]):
    """Serviço para operações relacionadas a usuários."""

    def __init__(
        self,
        repository: UserRepository = Depends(),
        mailgun: MailGun = Depends(),
        unit_of_work: UnitOfWork = Depends(),
        session_repository: SessionRepository = Depends(),
    ):
        super().__init__(repository, User, unit_of_work)
        self.mailgun = mailgun
        self.repository = repository
        self.handlers = handlers
        self.session_repository = session_repository
