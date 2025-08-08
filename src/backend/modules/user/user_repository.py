from fastapi.params import Depends
from wireup import service

from backend.core.database import DatabaseConnection
from backend.models.user import User
from backend.modules.base.base_repository import BaseRepository


@service(lifetime="scoped")
class UserRepository(BaseRepository[User]):
    """
    Repositório para operações relacionadas a usuários.
    """

    def __init__(self, connection: DatabaseConnection = Depends()):
        super().__init__(User, connection)
