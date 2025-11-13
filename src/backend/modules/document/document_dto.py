"""DTOs para operações de criação de documentos."""

import json
from typing import List, Optional

from pydantic import HttpUrl, field_serializer, model_validator
from sqlmodel import AutoString, Field, SQLModel

from backend.core.validators import MetadataDict
from backend.modules.base.base_dto import ModelBase
from backend.modules.document.document_enums import DocumentKind


# TODO: Passar responsabilidade de extrair informações para o LLM
class DocumentBase(SQLModel):
    """Modelo base para DTO de documentos com validações de tamanho e estrutura."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    kind: DocumentKind
    source: str = Field(min_length=1, max_length=100)
    url: Optional[HttpUrl] = Field(default=None, sa_type=AutoString)
    keywords: List[str] = Field(default_factory=list, max_length=25)
    meta: Optional[MetadataDict] = Field(default_factory=dict)


class DocumentIngestRequest(DocumentBase):
    """Payload para criação de um documento a partir de texto puro."""

    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        """Converte de JSON string para dict se necessário."""
        if isinstance(value, str):
            return cls(**json.loads(value))

        return value

    @field_serializer('url')
    def serialize_url(self, value):
        """Serializa URL como string."""
        if value is not None:
            return str(value)

        return None


class DocumentIngestResponse(DocumentBase, ModelBase):
    """Resposta de ingestão de arquivo com chunks processados."""

    total_chunks: int


class ExtractedContent(SQLModel):
    """Conteúdo extraído do documento pelo LLM."""

    title: str = Field()
    source: str = Field()
    authors: List[str] = Field(default_factory=list, max_items=10)
    date: Optional[str] = Field(default=None, max_length=50)
    summary: str = Field(max_length=4000)
    keywords: List[str] = Field(default_factory=list, max_items=25)
    kind: DocumentKind = Field()


class DocumentIngestMetadata(SQLModel):
    """Metadados extraídos pelo LLM do documento."""

    content: Optional[ExtractedContent] = Field(default=None)
    should_reject: bool = Field(default=True)


class AIDocumentIngestResponse(ModelBase):
    """Resposta de ingestão via LLM com metadados extraídos."""

    document_id: str = Field()
    extracted_metadata: DocumentIngestMetadata = Field()
    total_chunks: int = Field()
