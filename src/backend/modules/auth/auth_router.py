from fastapi.params import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from wireup import service

from backend.modules.user.user_service import UserService

auth_router = InferringRouter(prefix="/auth", tags=["Auth"])


@service(lifetime="scoped")
@cbv(auth_router)
class AuthRouter:
    """Router para serviços de autenticação"""

    def __init__(self, user_service: UserService = Depends()):
        self.user_service = user_service

    # TODO: Ajustar para chamar o método correto de convite
    @auth_router.post("/invite")
    async def test_email(self, content: str) -> bool:
        """Endpoint para convidar usuário para a plataforma"""
        return await self.user_service.send_test_email(content)
