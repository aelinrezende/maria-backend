from datetime import datetime
from typing import Optional

from sqlmodel import Column, DateTime, Enum, Field

from backend.modules.user.user_enums import UserStatus

from .base import BaseModel


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
