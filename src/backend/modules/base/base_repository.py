from typing import Generic, TypeVar

from fastapi.params import Depends
from sqlalchemy import ColumnExpressionArgument
from sqlmodel import select
from sqlmodel.sql.expression import SelectOfScalar

from backend.core.database import DatabaseConnection
from backend.core.exceptions import EntityNotFoundException
from backend.models.base import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    """
    Classe base para repositórios, fornecendo métodos comuns para interação com o banco de dados.
    """

    def __init__(self, model: type[T], connection: DatabaseConnection = Depends()):
        self.__session = connection.session
        self.model = model

    @property
    def query(self) -> SelectOfScalar[T]:
        """Retorna o construtor de consultas para a sessão atual."""
        return select(self.model)

    async def insert(self, entity: T) -> T:
        """
        Cria uma nova entidade no banco de dados.

        :param entity: Entidade a ser criada.
        :return: Entidade criada.
        """
        self.__session.add(entity)

        return entity

    async def update(self, entity: T) -> T:
        """
        Atualiza uma entidade existente no banco de dados.

        :param entity: Entidade a ser atualizada.
        :return: Entidade atualizada.
        """
        await self.__session.merge(entity)

        return entity

    async def find_by_id(self, id: str) -> T | None:
        """
        Busca uma entidade pelo seu ID.

        :param id: ID da entidade a ser buscada.
        :return: Entidade encontrada ou None se não existir.

        :rtype: T | None

        :raises ValueError: Se a entidade não for encontrada.
        """
        return await self.__session.get(T, id)

    async def find_by_id_or_fail(self, id: str) -> T:
        """
        Busca uma entidade pelo seu ID.

        :param id: ID da entidade a ser buscada.
        :return: Entidade encontrada.
        :raises EntityNotFoundException: Se a entidade não for encontrada.
        """
        entity = await self.__session.get(T, id)

        if entity is None:
            raise EntityNotFoundException(
                entity_name=self.model.__name__,
                identifier=id
            )

        return entity

    async def find_one(self, *expression: ColumnExpressionArgument[bool] | bool) -> T | None:
        """
        Busca uma entidade com base em critérios especificados.

        :param kwargs: Critérios de busca.
        :return: Entidade encontrada ou None se não existir.
        """
        return (await self.__session.execute(self.query.where(*expression))).first()

    async def find_one_or_fail(self, *expression: ColumnExpressionArgument[bool] | bool) -> T:
        """
        Busca uma entidade com base em critérios especificados.
        
        :param expression: Critérios de busca.
        :return: Entidade encontrada.
        :raises EntityNotFoundException: Se a entidade não for encontrada.
        """
        entity = (await self.__session.execute(self.query.where(*expression))).first()

        if entity is None:
            raise EntityNotFoundException(
                entity_name=self.model.__name__
            )

        return entity

    async def find_many(
        self,  #
        *expression: ColumnExpressionArgument[bool] | bool
    ) -> list[T]:
        """
        Busca várias entidades com base em critérios especificados.

        :param kwargs: Critérios de busca.
        :return: Lista de entidades encontradas.
        """
        return (await self.__session.execute(self.query.where(*expression))).all()
