"""
Modelo para documentos da base de conhecimento
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import JSON, Column, Enum
from sqlmodel import Field, Relationship

from backend.models.base import BaseModel
from backend.models.user import User
from backend.modules.document.document_enums import DocumentKind

if TYPE_CHECKING:
    from backend.models.chunk import Chunk


class Document(BaseModel, table=True):
    """Modelo para documentos da base de conhecimento"""

    # Relacionamentos
    chunks: list["Chunk"] = Relationship(back_populates="document")
    author: Optional[User] = Relationship(cascade_delete=False)
    author_id: Optional[str] = Field(nullable=True, foreign_key="user.id")

    # Informações básicas
    title: str = Field(nullable=False, index=True)

    # Categorização
    keywords: List[str] = Field(
        sa_column=Column(JSON, nullable=False), default_factory=list,
    )
    kind: DocumentKind = Field(sa_column=Column(
        Enum(DocumentKind), nullable=False)
    )

    # Metadados
    source: str = Field(nullable=False, index=True)
    url: Optional[str] = Field(nullable=True)

    # Validação
    is_validated: bool = Field(nullable=False, default=False)
    validated_by: Optional[str] = Field(nullable=True)
    validated_at: Optional[datetime] = Field(nullable=True)

    # Configurações
    is_active: bool = Field(nullable=False, default=True)

    # Metadados adicionais
    meta: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=True),
    )
