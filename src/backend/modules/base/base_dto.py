from datetime import datetime
from typing import Generic, Optional, TypeVar

from pydantic import ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel
from sqlmodel import SQLModel

from backend.core.config import settings

T = TypeVar('T')


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


class PaginatedResponse(BaseResponse, Generic[T]):
    """Resposta paginada genérica."""
    data: list[T] = Field(
        description="Lista de itens da página atual"
    )
    has_next: bool = Field(
        description="Indica se existem mais itens disponíveis"
    )
    cursor_next: Optional[datetime] = Field(
        default=None,
        description="Cursor para a próxima página de resultados"
    )

    @model_validator(mode="after")
    def validate_cursor_consistency(self) -> "PaginatedResponse[T]":
        """Valida que cursor_next é None quando não há próximos resultados."""
        if not self.has_next:
            self.cursor_next = None

        return self


class PaginateRequest(BaseRequest):
    """Requisição de paginação genérica com cursor."""
    cursor: Optional[datetime] = Field(
        default=None,
        description="Cursor timestamp para paginação (formato ISO 8601)"
    )
    limit: int = Field(
        default=settings.PAGINATION_LIMIT,
        ge=1,
        le=50,
        description="Número máximo de itens a retornar (1-50)"
    )
