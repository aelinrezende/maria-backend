"""DTOs para operações de criação de documentos."""

from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl

from backend.core.validators import MetadataDict
from backend.modules.base.base_dto import ModelBase
from backend.modules.document.document_enums import DocumentKind


class DocumentBase(BaseModel):
    """Modelo base para DTO de documentos com validações de tamanho e estrutura."""

    title: str = Field(min_length=1, max_length=200)
    kind: DocumentKind
    source: str = Field(min_length=1, max_length=100)
    url: Optional[HttpUrl] = Field(default=None)
    keywords: List[str] = Field(
        default_factory=list, max_length=25
    )
    metadata: MetadataDict = Field(default_factory=dict)


class DocumentCreateTextRequest(DocumentBase):
    """Payload para criação de um documento a partir de texto puro."""

    content: str = Field(min_length=1, max_length=100_000)


class DocumentCreateTextResponse(ModelBase, DocumentBase):
    """Resposta de criação de documento."""

    content: str
