from dataclasses import dataclass
from typing import Generic, TypeVar

from backend.models.base import BaseModel
from backend.modules.base.base_repository import BaseRepository

T = TypeVar("T", bound=BaseModel)


@dataclass
class BaseService(Generic[T]):
    """
    Classe base para serviços, fornecendo métodos comuns para regras de negócio e lógica de aplicação.
    """

    def __init__(self, repository: BaseRepository[T], model: type[T]):
        self.repository = repository
        self.model = model

    async def create(self, dto: dict) -> T:
        """
        Cria uma nova entidade no banco de dados.

        :param dto: DTO da entidade a ser criada.
        :return: Entidade criada.
        """
        entity = self.model(**dto)
        await self.repository.insert(entity)

        return entity

    async def update(self, id: str, dto: dict) -> T:
        """
        Atualiza uma entidade existente no banco de dados.

        :param id: ID da entidade a ser atualizada.
        :param dto: DTO com os novos dados da entidade.
        :return: Entidade atualizada.
        """
        entity = await self.repository.find_by_id_or_fail(id)

        await self.repository.update(self.model(**dto, id=entity.id))

        return entity
