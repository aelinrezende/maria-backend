from typing import TYPE_CHECKING, List

from backend.models.chunk import Chunk
from backend.services.chunking.models import PaperChunk

if TYPE_CHECKING:
    from backend.modules.chunk.chunk_hub import ChunkHub


async def create_chunks_with_embeddings(
    hub: "ChunkHub",
    document_id: str,
    chunked_pages: List[PaperChunk]
) -> List[Chunk]:
    """Cria chunks com embeddings para um documento."""
    # Extrai o texto de cada página
    chunks_text = [page.content for page in chunked_pages]

    # Gera embeddings para todos os chunks
    embeddings = await hub.embeddings_provider.embed_passages(chunks_text)

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
    return hub.repository.insert_multiple(chunks)
