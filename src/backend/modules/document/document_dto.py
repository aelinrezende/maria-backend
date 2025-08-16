"""DTOs para operações de criação de documentos."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from backend.modules.base.base_dto import ModelBase
from backend.modules.document.document_enums import DocumentKind


class DocumentBase(BaseModel):
    """Modelo base para DTO de documentos."""

    title: str
    kind: DocumentKind
    source: str
    keywords: List[str] = Field(default_factory=list)
    url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentCreateTextRequest(DocumentBase):
    """Payload para criação de um documento a partir de texto puro."""

    content: str = Field(min_length=1)


class DocumentCreateTextResponse(ModelBase, DocumentBase):
    """Resposta de criação de documento."""

    content: str
