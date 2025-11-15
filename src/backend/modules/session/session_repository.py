from fastapi.params import Depends
from wireup import service

from backend.core.database import DatabaseConnection
from backend.models.session import Session
from backend.modules.base.base_repository import BaseRepository


@service(lifetime="scoped")
class SessionRepository(BaseRepository[Session]):
    """
    Repositório para operações relacionadas a sessões.
    """

    def __init__(self, connection: DatabaseConnection = Depends()):
        super().__init__(Session, connection)

    async def get_by_token(self, token: str) -> Session | None:
        """
        Busca sessão pelo token JWT.

        Args:
            token: Token JWT a ser buscado

        Returns:
            Session | None: Sessão encontrada ou None
        """
        return await self.find_one(self.model.token == token)
