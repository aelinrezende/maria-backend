from typing import Generic, List, TypeVar

from fastapi.params import Depends
from sqlalchemy import ColumnExpressionArgument
from sqlmodel import select
from sqlmodel.sql.expression import SelectOfScalar

from backend.core.database import AsyncSession, DatabaseConnection
from backend.exceptions import NotFoundException
from backend.models.base import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    """
    Classe base para repositórios, fornecendo métodos comuns para interação com o banco de dados.

    :param model: O modelo de dados associado a este repositório.
    :param connection: A conexão com o banco de dados.
    """

    def __init__(self, model: type[T], connection: DatabaseConnection = Depends()):
        self.__session: AsyncSession = connection.session
        self.model: type[T] = model

    @property
    def query(self) -> SelectOfScalar[T]:
        """Retorna o construtor de consultas para a sessão atual."""
        return select(self.model)

    def insert(self, entity: T) -> T:
        """
        Cria uma nova entidade no banco de dados.

        :param entity: Entidade a ser criada.
        :return: Entidade criada.
        """
        self.__session.add(entity)

        return entity

    def insert_multiple(self, entities: List[T]) -> List[T]:
        """
        Cria novas entidades no banco de dados.

        :param entities: Lista de entidades a serem criadas.
        :return: Lista de entidades criadas.
        """
        self.__session.add_all(entities)

        return entities

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
        return await self.__session.get(self.model, id)

    async def find_by_id_or_fail(self, id: str) -> T:
        """
        Busca uma entidade pelo seu IDa.

        :param id: ID da entidade a ser buscada.
        :return: Entidade encontrada ou None se não existir.
        """
        entity = await self.__session.get(self.model, id)

        if entity is None:
            raise NotFoundException(f"{self.model.__name__.upper()}_NOT_FOUND")

        return entity

    async def find_one(self, *expression: ColumnExpressionArgument[bool] | bool) -> T | None:
        """
        Busca uma entidade com base em critérios especificados.

        :param kwargs: Critérios de busca.
        :return: Entidade encontrada ou None se não existir.
        """
        return (await self.__session.execute(self.query.where(*expression))).scalar_one_or_none()

    async def find_one_or_fail(self, *expression: ColumnExpressionArgument[bool] | bool) -> T:
        """
        Busca uma entidade com base em critérios especificados.
        :param kwargs: Critérios de busca.
        :return: Entidade encontrada ou None se não existir.
        """
        entity = (await self.__session.execute(self.query.where(*expression))).scalar_one_or_none()

        if entity is None:
            raise NotFoundException(f"{self.model.__name__.upper()}_NOT_FOUND")

        return entity

    async def find_many(
        self,  #
        *expression: ColumnExpressionArgument[bool] | bool
    ) -> List[T]:
        """
        Busca várias entidades com base em critérios especificados.

        :param kwargs: Critérios de busca.
        :return: Lista de entidades encontradas.
        """
        return (await self.__session.execute(self.query.where(*expression))).scalars().all()

    def run(
        self,
        scalar: SelectOfScalar[T],
    ):
        """
        Executa uma consulta SQLAlchemy fornecida usando a sessão atual.

        :param scalar: Consulta SQLAlchemy (SelectOfScalar) a ser executada.
        :return: Resultado da execução da consulta.
        :rtype: sqlalchemy.engine.Result

        Use este método quando precisar executar manualmente uma consulta personalizada,
        ao invés dos métodos utilitários como find_one ou find_many, para obter maior controle sobre a execução.
        """
        return self.__session.execute(scalar)
