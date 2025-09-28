from typing import List

from fastapi.params import Depends
from wireup import service

from backend.core import UnitOfWork
from backend.integrations.embeddings import LocalSentenceTransformerProvider
from backend.models.chunk import Chunk
from backend.modules.base.base_service import BaseService
from backend.modules.chunk.chunk_repository import ChunkRepository
from backend.services.chunking.models import PaperChunk


@service(lifetime="scoped")
class ChunkService(BaseService[Chunk]):
    """Camada de regras de negócio para `Chunk`."""

    def __init__(
        self,
        repository: ChunkRepository = Depends(),
        embeddings: LocalSentenceTransformerProvider = Depends(),
        unit_of_work: UnitOfWork = Depends(),
    ):
        super().__init__(repository, Chunk, unit_of_work)
        self._embeddings_provider = embeddings

    async def create_chunks_with_embeddings(
        self,
        document_id: str,
        chunked_pages: List[PaperChunk]
    ) -> List[Chunk]:
        """Cria chunks com embeddings para um documento."""
        # Extrai o texto de cada página
        chunks_text = [page.content for page in chunked_pages]

        # Gera embeddings para todos os chunks
        embeddings = await self._embeddings_provider.embed_passages(chunks_text)

        # Gera tuplas de (página do chunk, embedding)
        tuples = zip(chunked_pages, embeddings)

        # Cria os objetos Chunk
        chunks = [
            Chunk(
                document_id=document_id,
                content=chunk.content,
                embedding=embedding,
                size=len(chunk.content),
                order=index,
                page=chunk.page,
            ) for index, (chunk, embedding) in enumerate(tuples)
        ]

        # Persiste os chunks no banco
        return self.repository.insert_multiple(chunks)
