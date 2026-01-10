

from fastapi.params import Depends
from wireup import service

from backend.core import UnitOfWork
from backend.integrations.llm.factory import LLMFactory
from backend.models.document import Document
from backend.modules.base.base_hub import BaseHub
from backend.modules.chunk.chunk_hub import ChunkHub
from backend.modules.document import handlers
from backend.modules.document.document_repository import DocumentRepository
from backend.services.chunking.smart_chunker import SmartChunker


@service(lifetime="scoped")
class DocumentHub(BaseHub[Document]):
    """Camada de regras de negócio para `Document`."""

    def __init__(
        self,
        repository: DocumentRepository = Depends(),
        unit_of_work: UnitOfWork = Depends(),
        chunk_hub: ChunkHub = Depends(),
    ):
        super().__init__(repository, Document, unit_of_work)
        self.chunk_hub = chunk_hub
        self.smart_chunker = SmartChunker()
        self.llm_provider = LLMFactory.create_provider()
        self.handlers = handlers
