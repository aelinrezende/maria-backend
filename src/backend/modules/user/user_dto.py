from backend.modules.base.base_dto import ModelBase
from backend.modules.user.user_enums import UserStatus


class UserResponse(ModelBase):
    """DTO para resposta de dados do usuário"""

    name: str
    email: str
    status: UserStatus
