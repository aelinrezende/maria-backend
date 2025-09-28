"""Interface para o orquestrador inteligente de chunking."""
from typing import List, Optional, Protocol

from backend.modules.document.document_enums import DocumentKind
from backend.services.chunking.enums import ChunkingStrategy
from backend.services.chunking.models import PaperChunk
from backend.services.converter.models import PaperPage


class ISmartChunker(Protocol):
    """Interface para orquestradores inteligentes de chunking."""

    def chunk_intelligently(
        self,
        papers_pages: List[PaperPage],
        document_kind: DocumentKind,
        force_strategy: Optional[ChunkingStrategy] = None
    ) -> List[PaperChunk]:
        """
        Executa chunking inteligente baseado no tipo de documento.

        Args:
            papers_pages: Páginas a serem divididas em chunks
            document_kind: Tipo de documento (área de foco do Mar.IA)
            force_strategy: Estratégia forçada (opcional, sobrescreve seleção automática)

        Returns:
            Resultado do chunking com metadata
        """
        ...
