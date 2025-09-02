from typing import Optional

from fastapi import Depends
from wireup import service

from backend.core.database import DatabaseConnection
from backend.models.base import BaseModel


@service(lifetime="scoped")
class UnitOfWork:
    """Implementa o padrão Unit of Work para gerenciar transações."""

    def __init__(self, connection: DatabaseConnection = Depends()):
        self.session = connection.session

    async def commit(self, entity: Optional[BaseModel] = None) -> None:
        """Confirma a transação atual."""
        await self.session.commit()

        if entity:
            await self.session.refresh(entity)
