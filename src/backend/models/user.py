from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Column, DateTime, Enum, Field, Relationship

from backend.modules.user.user_enums import UserStatus

from .base import BaseModel

if TYPE_CHECKING:
    from backend.models.message import Message
    from backend.models.session import Session


class User(BaseModel, table=True):
    """Modelo de usuário"""
    name: str = Field(nullable=False, max_length=100)
    password: Optional[str] = Field(nullable=True, default=None)
    email: Optional[str] = Field(nullable=True, max_length=255, unique=True)
    status: UserStatus = Field(
        sa_column=Column(Enum(UserStatus), nullable=False),
    )
    pronouns: Optional[str] = Field(nullable=True, max_length=20)
    invitation_code: Optional[str] = Field(
        nullable=True,
        default=None,
        max_length=10
    )
    invitation_code_expiration_date: Optional[datetime] = Field(
        nullable=True,
        default=None,
        sa_type=DateTime(timezone=True)
    )

    # Relacionamentos
    sessions: List["Session"] = Relationship(back_populates="user")
    messages: List["Message"] = Relationship(back_populates="user")
