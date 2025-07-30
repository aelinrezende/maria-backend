"""
Modelo base para todos os modelos do sistema
"""

from datetime import datetime, timezone
from uuid import uuid4

from sqlmodel import DateTime, Field, SQLModel


class BaseModel(SQLModel):
    """Modelo base com campos comuns"""

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    created_at: datetime = Field(
        nullable=False,
        sa_type=DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
    )
    updated_at: datetime = Field(
        nullable=False,
        sa_type=DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
    )
