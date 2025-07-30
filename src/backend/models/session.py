from sqlalchemy import Column, Enum
from sqlmodel import Field

from backend.models.base import BaseModel
from backend.modules.session.session_enums import SessionStatus


class Session(BaseModel, table=True):
    """Modelo de sessão do usuário"""

    user_id: str = Field(nullable=False, foreign_key="user.id")
    token: str = Field(nullable=False, unique=True, index=True)
    status: SessionStatus = Field(
        sa_column=Column(Enum(SessionStatus, nullable=False)),
        default=SessionStatus.ACTIVE,
    )
