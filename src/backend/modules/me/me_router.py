"""Router para endpoints de perfil de usuário."""

from fastapi.params import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from wireup import service

from backend.cross_cutting.middleware.auth import authenticate
from backend.models.user import User
from backend.modules.me import handlers
from backend.modules.user.user_dto import UserResponse

me_router = InferringRouter(prefix="/me", tags=["Profile"])


@service(lifetime="scoped")
@cbv(me_router)
class MeRouter:
    """Router para serviços de perfil de usuário."""

    @me_router.get(
        "/",
        response_model=UserResponse,
        summary="Obter perfil do usuário"
    )
    async def get_profile(
        self,
        current_user: User = Depends(authenticate),
    ) -> UserResponse:
        """
        Obtém dados do perfil do usuário autenticado.

        Este endpoint retorna informações básicas do usuário logado,
        incluindo nome, e-mail e status. Requer autenticação JWT válida.
        """
        return handlers.get_profile(
            current_user
        )
