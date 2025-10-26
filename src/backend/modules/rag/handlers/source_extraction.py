"""Handler para extração de informações estruturadas de fontes dos chunks RAG."""

from typing import Dict, List

from backend.models.chunk import Chunk
from backend.modules.rag.rag_dto import SourceInfo


def extract_source_info(chunks: List[Chunk]) -> List[SourceInfo]:
    """Extrai informações estruturadas dos chunks para criar SourceInfo.

    Args:
        chunks: Lista de chunks similares encontrados pelo RAG
                (já limitada pela busca de chunks)

    Returns:
        Lista de SourceInfo com dados estruturados das fontes
    """
    if not chunks:
        return []

    # Agrupa chunks por documento para evitar duplicatas de fonte
    documents_by_source: Dict[str, Chunk] = {}

    for chunk in chunks:
        source = chunk.document.source

        if source not in documents_by_source:
            documents_by_source[source] = chunk

    # Cria SourceInfo para cada documento único, mantendo ordem de relevância
    sources = []

    for order, (source, chunk) in enumerate(documents_by_source.items(), 1):
        sources.append(
            SourceInfo(
                title=source,
                category=chunk.document.kind.value,
                description=source[:200],
                order=order,
                url=chunk.document.url
            )
        )

    return sources
