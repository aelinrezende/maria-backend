

from fastapi import UploadFile
from fastapi.params import Depends
from wireup import service

from backend.core import UnitOfWork
from backend.integrations.llm.factory import LLMFactory
from backend.models.document import Document
from backend.modules.base.base_service import BaseService
from backend.modules.chunk.chunk_service import ChunkService
from backend.modules.document.document_dto import (
    DocumentIngestRequest,
    DocumentIngestResponse,
)
from backend.modules.document.document_repository import DocumentRepository
from backend.services.chunking.smart_chunker import SmartChunker
from backend.services.converter import document_to_markdown
from backend.services.converter.metadata_extractor import MetadataExtractor


@service(lifetime="scoped")
class DocumentService(BaseService[Document]):
    """Camada de regras de negócio para `Document`."""

    def __init__(
        self,
        repository: DocumentRepository = Depends(),
        unit_of_work: UnitOfWork = Depends(),
        chunk_service: ChunkService = Depends(),
    ):
        super().__init__(repository, Document, unit_of_work)
        self.chunk_service = chunk_service
        self.smart_chunker = SmartChunker()
        self.llm_provider = LLMFactory.create_provider()

    async def ingest_file(
        self,
        document_file: UploadFile,
        dto: DocumentIngestRequest,
    ) -> None:
        """Ingere um arquivo, criando documento e chunks com embeddings."""

        # 1. Converte arquivo para Markdown
        metadata: MetadataExtractor = document_to_markdown(
            document_file
        )

        dto.title = dto.title or metadata.title or "Sem título"
        dto.meta.update(metadata.metadata or {})

        # 2. Processa com Smart Chunker
        chunked_pages = self.smart_chunker.chunk_intelligently(
            metadata.pages, dto.kind
        )

        # 3. Cria o documento no banco
        document = self.repository.insert(Document(**dto.model_dump()))

        # 4. Cria os chunks com embeddings
        saved_chunks = await self.chunk_service.create_chunks_with_embeddings(
            document.id, chunked_pages
        )

        await self.unit_of_work.commit()

        return DocumentIngestResponse(
            **document.model_dump(),
            total_chunks=len(saved_chunks),
        )
