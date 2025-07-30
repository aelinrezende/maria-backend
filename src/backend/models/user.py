from typing import Optional

from sqlmodel import Column, Enum, Field

from backend.modules.user.user_enums import UserStatus

from .base import BaseModel


class User(BaseModel, table=True):
    name: str = Field(nullable=False, max_length=100)
    username: str = Field(nullable=False, max_length=100, unique=True)
    password: str = Field(nullable=False)
    status: UserStatus = Field(
        sa_column=Column(Enum(UserStatus), nullable=False),
    )
    pronouns: Optional[str] = Field(nullable=True, max_length=20)
    invitation_code: Optional[str] = Field(
        nullable=True,
        default=None,
        max_length=10
    )
