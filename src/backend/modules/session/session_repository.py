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
