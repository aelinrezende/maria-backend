
from fastapi import Body, Depends, UploadFile
from fastapi.params import File
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from wireup import service as inject

from backend.models import Document
from backend.modules.base.base_router import get_base_router
from backend.modules.document.document_dto import (
    AIDocumentIngestResponse,
    DocumentIngestRequest,
    DocumentIngestResponse,
)
from backend.modules.document.document_hub import DocumentHub

document_router = InferringRouter(prefix="/documents", tags=["Documents"])
BaseRouter = get_base_router(document_router)


@inject(lifetime="scoped")
@cbv(document_router)
class DocumentRouter(BaseRouter[Document]):
    """Endpoints para criação e manipulação de documentos."""

    def __init__(self, hub: DocumentHub = Depends()):
        super().__init__(hub)
        self.hub = hub

    @document_router.post(
        "/ingest/file",
        response_model=DocumentIngestResponse,
        summary="Ingerir arquivo e criar documento com chunks"
    )
    # TODO: Validar arquivo (tamanho, tipo, etc.)
    async def ingest_file(
        self,
        document_file: UploadFile = File(...),
        dto: DocumentIngestRequest = Body(...),
    ) -> DocumentIngestResponse:
        """
        Ingere um arquivo, convertendo para Markdown, aplicando chunking inteligente,
        gerando embeddings e persistindo no banco de dados.

        Args:
            document_file: Arquivo a ser processado
            dto: Dados do documento (título, tipo, fonte, etc.)

        Returns:
            Informações do documento criado com chunks e embeddings
        """

        return await self.hub.handlers.ingest_file(self.hub, document_file, dto)

    @document_router.post(
        "/ingest/ai_file",
        response_model=AIDocumentIngestResponse,
        summary="Ingerir arquivo com extração automática de metadados via LLM"
    )
    async def ingest_ai_file(
        self,
        document_file: UploadFile = File(...)
    ) -> AIDocumentIngestResponse:
        """
        Ingere um arquivo usando LLM para extrair metadados automaticamente.
        O LLM analisa as primeiras páginas para extrair título, autor, data, resumo,
        palavras-chave e tipo do documento.

        Args:
            document_file: Arquivo a ser processado

        Returns:
            Documento criado com metadados extraídos pelo LLM e chunks processados
        """
        return await self.hub.handlers.ingest_file_by_ai(self.hub, document_file)
