
from fastapi.params import Depends
from wireup import service

from backend.core.config import settings
from backend.integrations.mailgun import MailGun
from backend.models.user import User
from backend.modules.base.base_service import BaseService
from backend.modules.user.user_repository import UserRepository


@service(lifetime="scoped")
class UserService(BaseService[User]):
    def __init__(self, repository: UserRepository = Depends(), mailgun: MailGun = Depends()):
        super().__init__(repository, User)
        print("Inicializando UserService com Mailgun")
        self.mailgun = mailgun

    # TODO: Remover no futuro
    async def send_test_email(self, content: str) -> bool:
        print(f"Enviando email de teste {self.mailgun}")
        return await self.mailgun.send_email(
            settings.MAILGUN_TEST_EMAIL,
            "Teste de Email",
            content
        )
