"""DTOs relacionados a sessões de usuário"""


from backend.modules.base.base_dto import ModelBase
from backend.modules.session.session_enums import SessionStatus
from backend.modules.user.user_dto import UserResponse


class SessionResponse(ModelBase):
    """DTO para resposta de dados da sessão"""

    user: UserResponse
    token: str
    status: SessionStatus
