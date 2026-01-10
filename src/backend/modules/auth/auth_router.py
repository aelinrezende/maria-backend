from fastapi.params import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from wireup import service

from backend.modules.auth.auth_dto import (
    CompleteRegistrationRequest,
    InviteRequest,
    LoginRequest,
    ValidateInviteRequest,
)
from backend.modules.auth.auth_hub import AuthHub
from backend.modules.session.session_dto import SessionResponse
from backend.modules.user.user_dto import UserResponse
from backend.modules.user.user_hub import UserHub

auth_router = InferringRouter(prefix="/auth", tags=["Auth"])


@service(lifetime="scoped")
@cbv(auth_router)
class AuthRouter:
    """Router para serviços de autenticação"""

    def __init__(self, hub: AuthHub = Depends(), user_hub: UserHub = Depends()):
        self.hub = hub
        self.user_hub = user_hub

    @auth_router.post("/invite", summary="Enviar convite de usuário")
    async def send_invitation(self, request: InviteRequest) -> bool:
        """
        Envia um convite para novo usuário acessar a plataforma.
        """
        return await self.user_hub.handlers.send_invitation(self.user_hub, request)

    @auth_router.post("/validate_invitation_code", summary="Validar código de convite")
    async def validate_invitation(self, request: ValidateInviteRequest) -> UserResponse:
        """
        Valida um código de convite enviado por e-mail.
        """
        return await self.user_hub.handlers.validate_invitation(
            self.user_hub,
            request.invitation_code
        )

    @auth_router.post(
        "/login",
        response_model=SessionResponse,
        summary="Login de usuário"
    )
    async def login(self, request: LoginRequest) -> SessionResponse:
        """
        Autentica usuário existente e cria sessão.

        Este endpoint permite que usuários já cadastrados façam login
        fornecendo e-mail e senha. Um token JWT será gerado para acesso.
        """
        return await self.hub.handlers.login(self.user_hub, request)

    @auth_router.post(
        "/complete_registration/{invitation_code}",
        response_model=SessionResponse,
        summary="Finalizar cadastro de usuário"
    )
    async def complete_registration(
        self,
        invitation_code: str,
        request: CompleteRegistrationRequest
    ) -> SessionResponse:
        """
        Finaliza o cadastro de usuário com base em convite válido.

        Este endpoint permite que um usuário convidado complete seu cadastro
        fornecendo nome, pronomes e senha. Um token JWT será gerado para acesso.
        """
        return await self.user_hub.handlers.complete_registration(
            self.user_hub,
            invitation_code,
            request
        )
