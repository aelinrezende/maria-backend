

from typing import Annotated, Dict, Generic, List, Literal, Optional, TypeVar

from fastapi.params import Depends, Query
from fastapi_utils.inferring_router import InferringRouter

from backend.models.base import BaseModel
from backend.modules.base.base_dto import PaginateRequest
from backend.modules.base.base_service import BaseService

T = TypeVar("T", bound=BaseModel)

Methods = Literal["get", "create", "update", "delete", "list"]


class _EndpointEntry():
    path: str
    verb: str

    def __init__(self, path: str, verb: str):
        self.path = path
        self.verb = verb


_endpoints: Dict[Methods, _EndpointEntry] = {
    "get": _EndpointEntry("/{id}", "GET"),
    "create": _EndpointEntry("/", "POST"),
    "update": _EndpointEntry("/{id}", "PATCH"),
    "delete": _EndpointEntry("/{id}", "DELETE"),
    "list": _EndpointEntry("/", "GET"),
}


def get_base_router(
    router: InferringRouter,
    exclude: Optional[List[Methods]] = None
):
    """
    Função para obter o router base.

    Args:
        router: Instância do router FastAPI
        exclude: Lista de métodos a serem excluídos/sobrescritos

    Returns:
        BaseRouter: Classe do router base genérico.
    """

    class BaseRouter(Generic[T]):
        """Router base genérico para operações CRUD."""

        def __init__(self, service: BaseService[T] = Depends()):
            self.service = service

        @router.get(_endpoints["list"].path)
        async def list(self, request: Annotated[PaginateRequest, Query()]) -> list[T]:
            """Endpoint para listar recursos com paginação e filtros.
            Returns:
                list[T]: Lista de recursos.
            """
            # TODO: Implementar lógica de listagem com paginação e filtros
            raise NotImplementedError("List method not implemented")

        @router.get(_endpoints["get"].path)
        async def get(self, id: str) -> T:
            """Endpoint para obter um recurso específico.
            Args:
                id (str): ID do recurso.
            Returns:
                T: Instância do recurso solicitado.
            """
            # TODO: Implementar lógica de obtenção de recurso por ID
            raise NotImplementedError("Get method not implemented")

        @router.post(_endpoints["create"].path)
        async def create(self, dto) -> T:
            """
            Endpoint para criar um recurso.
            Returns:
                T: Instância do recurso criado.
            """
            await self.service.create(dto.model_dump())

        @router.patch(_endpoints["update"].path)
        async def update(self) -> T:
            """
            Endpoint para atualizar um recurso.
            Returns:
                T: Instância do recurso atualizado.
            """
            # TODO: Implementar lógica de atualização
            raise NotImplementedError("Update method not implemented")

        @router.delete(_endpoints["delete"].path)
        async def delete(self, id: str) -> None:
            """Endpoint para excluir um recurso.
            Args:
                id (str): ID do recurso a ser excluído.
            Returns:
                None: Confirmação de exclusão.
            """
            # TODO: Implementar lógica de exclusão
            raise NotImplementedError("Delete method not implemented")

    _remove_endpoints(router, exclude)

    return BaseRouter


def _remove_endpoints(
    router: InferringRouter,
    exclude: Optional[List[Methods]] = None
):
    if not exclude:
        return

    for id, entry in _endpoints.items():
        if id in exclude:
            router.routes = [
                route for route in router.routes
                if not (
                    route.path == f"{router.prefix}{entry.path}" and entry.verb in route.methods
                )

            ]
