from typing import Generic, TypeVar

from backend.core.unit_of_work import UnitOfWork
from backend.models.base import BaseModel
from backend.modules.base.base_repository import BaseRepository

T = TypeVar("T", bound=BaseModel)


class BaseService(Generic[T]):
    """
    Classe base para serviços, fornecendo métodos comuns para regras de negócio e lógica de aplicação.
    """

    def __init__(self, repository: BaseRepository[T], model: type[T], unit_of_work: UnitOfWork):
        self.repository = repository
        self.model = model
        self.unit_of_work = unit_of_work

    async def create(self, dto: dict) -> T:
        """
        Cria uma nova entidade no banco de dados.

        :param dto: DTO da entidade a ser criada.
        :return: Entidade criada.
        """
        entity = self.model(**dto)

        self.repository.insert(entity)
        await self.unit_of_work.commit()

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
