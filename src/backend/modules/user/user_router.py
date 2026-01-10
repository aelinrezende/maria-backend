
from fastapi.params import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from wireup import service as inject

from backend.models.user import User
from backend.modules.base.base_router import get_base_router
from backend.modules.user.user_hub import UserHub

user_router = InferringRouter(prefix="/users", tags=["Users"])
BaseRouter = get_base_router(user_router)


@inject(lifetime="scoped")
@cbv(user_router)
class UserRouter(BaseRouter[User]):
    """Router para o modelo de usuário"""

    def __init__(self, hub: UserHub = Depends()):
        """Inicializa o router com serviços"""
        super().__init__(hub)
