from fastapi.params import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from wireup import service

from backend.modules.auth.auth_dto import (
    InviteRequest,
    ValidateInviteRequest,
)
from backend.modules.user.user_dto import UserResponse
from backend.modules.user.user_service import UserService

auth_router = InferringRouter(prefix="/auth", tags=["Auth"])


@service(lifetime="scoped")
@cbv(auth_router)
class AuthRouter:
    """Router para serviços de autenticação"""

    def __init__(self, user_service: UserService = Depends()):
        self.user_service = user_service

    @auth_router.post("/invite", summary="Enviar convite de usuário")
    async def send_invitation(self, request: InviteRequest) -> bool:
        """
        Envia um convite para novo usuário acessar a plataforma.
        """
        return await self.user_service.handlers.send_invitation(self.user_service, request)

    @auth_router.post("/validate_invitation_code", summary="Validar código de convite")
    async def validate_invitation(self, request: ValidateInviteRequest) -> UserResponse:
        """
        Valida um código de convite enviado por e-mail.
        """
        return await self.user_service.handlers.validate_invitation(
            self.user_service,
            request.invitation_code
        )
