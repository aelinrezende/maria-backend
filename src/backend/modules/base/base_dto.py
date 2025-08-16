from typing import Optional

from pydantic import BaseModel


class ModelBase(BaseModel):
    """Modelo base para DTOs."""

    id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
