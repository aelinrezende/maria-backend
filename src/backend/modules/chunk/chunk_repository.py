from typing import Callable, List, Optional

from fastapi.params import Depends
from sqlmodel.sql.expression import SelectOfScalar
from wireup import service

from backend.core import settings
from backend.core.database import DatabaseConnection
from backend.models.chunk import Chunk
from backend.modules.base.base_repository import BaseRepository

Builder = Callable[[SelectOfScalar[Chunk]], SelectOfScalar[Chunk]]


@service(lifetime="scoped")
class ChunkRepository(BaseRepository[Chunk]):
    """Repositório para operações de banco relacionadas a `Chunk`."""

    def __init__(self, connection: DatabaseConnection = Depends()):
        super().__init__(Chunk, connection)

    async def get_similar(
        self, embedding: List[float],
        builder: Optional[Builder] = None
    ) -> List[Chunk]:
        """Busca chunks similares baseado em um embedding fornecido.

        Args:
            embedding: Vetor de embedding para busca
            builder: Função opcional para modificar a query
        """

        query = self.query.order_by(
            Chunk.embedding.cosine_distance(  # pylint: disable=no-member
                embedding
            )
        ).limit(settings.RAG_TOP_K_CHUNKS)

        if builder:
            query = builder(query)

        result = await self.run(
            query
        )

        return result.scalars().all()
