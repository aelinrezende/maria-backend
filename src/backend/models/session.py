from typing import TYPE_CHECKING

from sqlalchemy import Column, Enum
from sqlmodel import Field, Relationship

from backend.models.base import BaseModel
from backend.modules.session.session_enums import SessionStatus

if TYPE_CHECKING:
    from backend.models.user import User


class Session(BaseModel, table=True):
    """Modelo de sessão do usuário"""

    # Relacionamentos
    user_id: str = Field(
        nullable=False,
        foreign_key="user.id",
        ondelete="CASCADE",
        sa_column_kwargs={"name": "fk_session_user_id"}
    )
    user: "User" = Relationship(
        back_populates="sessions",
        sa_relationship_kwargs={"lazy": "joined"},
    )

    # Campos básicos
    token: str = Field(nullable=False, unique=True, index=True)
    status: SessionStatus = Field(
        sa_column=Column(Enum(SessionStatus, nullable=False)),
        default=SessionStatus.ACTIVE,
    )
