

from typing import Generic, TypeVar

from fastapi.params import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from backend.models.base import BaseModel
from backend.modules.base.base_service import BaseService

T = TypeVar("T", bound=BaseModel)


def get_base_router(router: InferringRouter):
    """Função para obter o router base"""

    @cbv(router)
    class BaseRouter(Generic[T]):
        def __init__(self, service: BaseService[T] = Depends()):
            self.service = service

        @router.get("/")
        async def list(self) -> list[T]:
            """Endpoint para listar recursos com paginação e filtros.
            Returns:
                list[T]: Lista de recursos.
            """
            # TODO: Implementar lógica de listagem com paginação e filtros
            raise NotImplementedError("List method not implemented")

        @router.get("/{id}")
        async def get(self, id: str) -> T:
            """Endpoint para obter um recurso específico.
            Args:
                id (str): ID do recurso.
            Returns:
                T: Instância do recurso solicitado.
            """
            # TODO: Implementar lógica de obtenção de recurso por ID
            raise NotImplementedError("Get method not implemented")

        @router.post("/")
        async def create(self, dto) -> T:
            """
            Endpoint para criar um recurso.
            Returns:
                T: Instância do recurso criado.
            """
            await self.service.create(dto.model_dump())

        @router.patch("/{id}")
        async def update(self) -> T:
            """
            Endpoint para atualizar um recurso.
            Returns:
                T: Instância do recurso atualizado.
            """
            # TODO: Implementar lógica de atualização
            raise NotImplementedError("Update method not implemented")

        @router.delete("/{id}")
        async def delete(self, id: str) -> None:
            """Endpoint para excluir um recurso.
            Args:
                id (str): ID do recurso a ser excluído.
            Returns:
                None: Confirmação de exclusão.
            """
            # TODO: Implementar lógica de exclusão
            raise NotImplementedError("Delete method not implemented")

    return BaseRouter
