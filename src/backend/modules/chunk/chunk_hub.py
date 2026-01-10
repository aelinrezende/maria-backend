from fastapi.params import Depends
from wireup import service

from backend.core import UnitOfWork
from backend.integrations.embeddings import LocalSentenceTransformerProvider
from backend.models.chunk import Chunk
from backend.modules.base.base_hub import BaseHub
from backend.modules.chunk import handlers
from backend.modules.chunk.chunk_repository import ChunkRepository


@service(lifetime="scoped")
class ChunkHub(BaseHub[Chunk]):
    """Camada de regras de negócio para `Chunk`."""

    def __init__(
        self,
        repository: ChunkRepository = Depends(),
        embeddings: LocalSentenceTransformerProvider = Depends(),
        unit_of_work: UnitOfWork = Depends(),
    ):
        super().__init__(repository, Chunk, unit_of_work)
        self.embeddings_provider = embeddings
        self.handlers = handlers
