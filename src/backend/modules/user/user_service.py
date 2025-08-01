from wireup import service

from backend.models.user import User
from backend.modules.base.base_service import BaseService
from backend.modules.user.user_repository import UserRepository


@service(lifetime="scoped")
class UserService(BaseService[User]):
    def __init__(self, repository: UserRepository):
        super().__init__(repository, User)
