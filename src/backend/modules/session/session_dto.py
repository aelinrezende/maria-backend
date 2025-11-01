"""DTOs relacionados a sessões de usuário"""

from datetime import datetime

from backend.models.base import BaseModel
from backend.modules.session.session_enums import SessionStatus


class SessionResponse(BaseModel):
    """DTO para resposta de dados da sessão"""

    user_id: str
    token: str
    status: SessionStatus
    created_at: datetime
    updated_at: datetime
