from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from wireup import service as inject

from backend.models import Document
from backend.modules.base.base_router import get_base_router
from backend.modules.document.document_dto import (
    DocumentCreateTextRequest,
    DocumentCreateTextResponse,
)
from backend.modules.document.document_service import DocumentService

document_router = InferringRouter(prefix="/documents", tags=["Documents"])
BaseRouter = get_base_router(document_router)


@inject(lifetime="scoped")
@cbv(document_router)
class DocumentRouter(BaseRouter[Document]):
    """Endpoints para criação e manipulação de documentos."""

    def __init__(self, service: DocumentService = Depends()):
        super().__init__(service)
        self.service = service

    @document_router.post(
        "/text", response_model=DocumentCreateTextResponse, summary="Criar documento a partir de texto bruto"
    )
    async def create_from_text(self, payload: DocumentCreateTextRequest) -> DocumentCreateTextResponse:
        """Cria documento a partir de texto puro e retorna eco dos dados principais."""
        return await self.service.ingest_text(payload)
