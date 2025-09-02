
from fastapi import UploadFile
from fastapi.params import Depends
from wireup import service

from backend.core import UnitOfWork
from backend.integrations.embeddings import (
    EmbeddingProvider,
    LocalSentenceTransformerProvider,
)
from backend.models.document import Document
from backend.modules.base.base_service import BaseService
from backend.modules.chunk.chunk_service import ChunkService
from backend.modules.document.document_dto import (
    DocumentIngestRequest,
    DocumentIngestResponse,
)
from backend.modules.document.document_repository import DocumentRepository
from backend.services.chunking.smart_chunker import SmartChunker
from backend.utils.converters import document_to_markdown


@service(lifetime="scoped")
class DocumentService(BaseService[Document]):
    """Camada de regras de negócio para `Document`."""

    def __init__(
        self,
        repository: DocumentRepository = Depends(),
        unit_of_work: UnitOfWork = Depends(),
        embeddings: LocalSentenceTransformerProvider = Depends(),
        chunk_service: ChunkService = Depends(),
    ):
        super().__init__(repository, Document, unit_of_work)
        self._embeddings_provider: EmbeddingProvider = embeddings
        self._chunk_service = chunk_service
        self._smart_chunker = SmartChunker()

    async def ingest_file(
        self,
        document_file: UploadFile,
        dto: DocumentIngestRequest,
    ) -> None:
        """Ingere um arquivo, criando documento e chunks com embeddings."""

        # 1. Converte arquivo para Markdown
        markdown_content = document_to_markdown(document_file)

        # 2. Processa com Smart Chunker
        chunks_text = self._smart_chunker.chunk_intelligently(
            markdown_content, dto.kind
        )

        # 3. Cria o documento no banco
        document = self.repository.insert(Document(**dto.model_dump()))

        # 4. Cria os chunks com embeddings
        saved_chunks = await self._chunk_service.create_chunks_with_embeddings(
            document.id, chunks_text
        )

        await self.unit_of_work.commit()

        return DocumentIngestResponse(
            **document.model_dump(),
            total_chunks=len(saved_chunks),
        )
