
from fastapi.params import Depends
from wireup import service

from backend.models.document import Document
from backend.modules.base.base_service import BaseService
from backend.modules.document.document_dto import (
    DocumentCreateTextRequest,
    DocumentCreateTextResponse,
)
from backend.modules.document.document_repository import DocumentRepository


@service(lifetime="scoped")
class DocumentService(BaseService[Document]):
    """Camada de regras de negócio para `Document`."""

    def __init__(self, repository: DocumentRepository = Depends()):
        super().__init__(repository, Document)

    async def ingest_text(self, dto: DocumentCreateTextRequest) -> DocumentCreateTextResponse:
        """Cria um documento a partir de texto bruto, gerando os chunks e realizando o embedding.

        :param dto: Dados de criação do documento.
        """
        return DocumentCreateTextResponse(**dto.model_dump())
