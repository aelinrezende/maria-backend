from typing import List

from fastapi.params import Depends
from wireup import service

from backend.core import UnitOfWork
from backend.integrations.embeddings import LocalSentenceTransformerProvider
from backend.models.chunk import Chunk
from backend.modules.base.base_service import BaseService
from backend.modules.chunk import ChunkRepository


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
        chunks_text: List[str]
    ) -> List[Chunk]:
        """Cria chunks com embeddings para um documento, adicionado-os
        a sessão para posterior persistência."""
        # Gera embeddings para todos os chunks
        embeddings = await self._embeddings_provider.embed_passages(chunks_text)

        # Gera tuplas de (texto do chunk, embedding)
        tuples = zip(chunks_text, embeddings)

        # Cria os objetos Chunk
        chunks = [
            Chunk(
                document_id=document_id,
                content=chunk_text,
                embedding=embedding,
                chunk_size=len(chunk_text),
                chunk_order=index
            ) for index, (chunk_text, embedding) in enumerate(tuples)
        ]

        # Persiste os chunks no banco
        return self.repository.insert_multiple(chunks)
