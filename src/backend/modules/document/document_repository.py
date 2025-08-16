from fastapi.params import Depends
from wireup import service

from backend.core.database import DatabaseConnection
from backend.models.document import Document
from backend.modules.base.base_repository import BaseRepository


@service(lifetime="scoped")
class DocumentRepository(BaseRepository[Document]):
    """Repositório para operações de banco relacionadas a `Document`."""

    def __init__(self, connection: DatabaseConnection = Depends()):
        super().__init__(Document, connection)
