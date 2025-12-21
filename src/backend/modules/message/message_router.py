"""Router para endpoints de mensagens."""

from typing import Annotated

from fastapi import Depends
from fastapi.params import Query
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from wireup import service as inject

from backend.cross_cutting.middleware.auth import authenticate
from backend.models.message import Message
from backend.modules.base.base_dto import PaginatedResponse, PaginateRequest
from backend.modules.base.base_router import get_base_router
from backend.modules.message import handlers
from backend.modules.message.message_service import MessageService

message_router = InferringRouter(prefix="/message", tags=["Messages"])
BaseRouter = get_base_router(message_router, exclude=["list"])


@inject(lifetime="scoped")
@cbv(message_router)
class MessageRouter(BaseRouter[Message]):
    """Router para operações relacionadas a mensagens."""

    def __init__(self, service: MessageService = Depends()):
        super().__init__(service)

    @message_router.get(
        "/",
        response_model=PaginatedResponse,
        summary="Listar mensagens do usuário",
        description="""
        Retorna as mensagens do usuário autenticado de forma paginada
        usando cursor-based pagination
        """
    )
    async def list(
        self,
        request: Annotated[PaginateRequest, Query()],
        _=Depends(authenticate)
    ) -> PaginatedResponse:
        """
        Endpoint para listar mensagens do usuário de forma paginada.

        Args:
            request: Parâmetros de paginação com cursor e limit

        Returns:
            Resposta paginada com mensagens do usuário
        """
        return await handlers.paginate_user_messages(self.service, request)
