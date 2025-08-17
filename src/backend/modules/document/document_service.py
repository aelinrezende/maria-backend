from fastapi.params import Depends
from loguru import logger
from wireup import service

from backend.integrations.embeddings import (
    EmbeddingProvider,
    LocalSentenceTransformerProvider,
)
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

    def __init__(
        self,
        repository: DocumentRepository = Depends(),
        embeddings: LocalSentenceTransformerProvider = Depends(),
    ):
        super().__init__(repository, Document)
        self._embeddings_provider: EmbeddingProvider = embeddings

    async def ingest_text(self, dto: DocumentCreateTextRequest) -> DocumentCreateTextResponse:
        """Cria um documento a partir de texto bruto, gerando os chunks e realizando o embedding."""
        vectors = await self._embeddings_provider.embed_passages([dto.content])
        embedding = vectors[0] if vectors and len(vectors) > 0 else []

        logger.debug(
            "Embedding gerado para documento: vectors={} dim={}",
            len(vectors),
            len(embedding) if embedding else 0,
        )

        return DocumentCreateTextResponse(**dto.model_dump())
