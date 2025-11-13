from datetime import datetime
from typing import Optional

from pydantic import ConfigDict
from pydantic.alias_generators import to_camel
from sqlmodel import SQLModel


class BaseRequest(SQLModel):
    """Modelo base para Requests."""
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )


class BaseResponse(SQLModel):
    """Modelo base para Responses."""
    model_config = ConfigDict(use_enum_values=True)


class ModelBase(BaseResponse):
    """Modelo base para DTOs."""
    model_config = ConfigDict(use_enum_values=True)

    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
