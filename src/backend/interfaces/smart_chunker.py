"""Interface para o orquestrador inteligente de chunking."""
from typing import List, Optional, Protocol

from backend.modules.document.document_enums import DocumentKind
from backend.services.chunking.enums import ChunkingStrategy


class ISmartChunker(Protocol):
    """Interface para orquestradores inteligentes de chunking."""

    def chunk_intelligently(
        self,
        text: str,
        document_kind: DocumentKind,
        force_strategy: Optional[ChunkingStrategy] = None
    ) -> List[str]:
        """
        Executa chunking inteligente baseado no tipo de documento.

        Args:
            text: Texto a ser dividido em chunks
            document_kind: Tipo de documento (área de foco do Mar.IA)
            force_strategy: Estratégia forçada (opcional, sobrescreve seleção automática)

        Returns:
            Resultado do chunking com metadata
        """
        ...
