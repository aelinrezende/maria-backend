
from fastapi_utils.inferring_router import InferringRouter

from backend.models.user import User
from backend.modules.base.base_router import get_base_router

user_router = InferringRouter(prefix="/users", tags=["Users"])
BaseRouter = get_base_router(user_router)


class UserRouter(BaseRouter[User]):
    """Router para o modelo de usuário"""

    def __init__(self):
        """Inicializa o router com serviços"""
