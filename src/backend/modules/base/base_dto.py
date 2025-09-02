from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel


class ModelBase(SQLModel):
    """Modelo base para DTOs."""

    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
