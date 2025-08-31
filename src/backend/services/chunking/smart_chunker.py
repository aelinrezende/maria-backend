"""Orquestrador inteligente para seleção de estratégias de chunking do Mar.IA."""
import re
from typing import List, Optional

from backend.interfaces.chunker import IChunker
from backend.interfaces.smart_chunker import ISmartChunker
from backend.modules.document.document_enums import DocumentKind
from backend.services.chunking import (
    AppChunkingConfig,
    ChunkingStrategy,
)
from backend.services.chunking.custom.custom_chunker import CustomChunker


class SmartChunker(ISmartChunker):
    """
    Orquestrador inteligente para as áreas específicas do Mar.IA.

    Seleciona automaticamente a melhor estratégia de chunking baseado no
    tipo de documento e características básicas do texto.
    """

    def __init__(self, chunker: IChunker = CustomChunker()):
        self.custom_chunker = chunker
        self.config = AppChunkingConfig()

    def chunk_intelligently(
        self,
        text: str,
        document_kind: DocumentKind,
        force_strategy: Optional[ChunkingStrategy] = None
    ) -> List[str]:
        """
        Executa chunking inteligente para as áreas do Mar.IA.

        Estratégia por área:
        - HORMONAL_SAFETY: SENTENCE (precisão médica)
        - LEGAL_PROCEDURES: SENTENCE (precisão legal)  
        - HEALTH_INSURANCE: PARAGRAPH (contexto de procedimentos)
        """
        if not text.strip():
            return []

        # 1. Seleciona estratégia
        strategy = force_strategy or self._select_strategy(text, document_kind)

        # 2. Obtém configuração específica
        config = self.config.get_config(document_kind)

        # 3. Executa chunking
        chunks = self._execute_chunking(text, strategy, config)

        # 4. Retorna resultado
        return chunks

    def _select_strategy(
        self,
        text: str,
        document_kind: DocumentKind
    ) -> ChunkingStrategy:
        """Seleciona a estratégia de chunking mais apropriada."""

        # Verifica se o texto tem estrutura formal mínima
        if not self._has_basic_structure(text):
            return ChunkingStrategy.SIZE

        # Estratégia baseada na configuração por área
        config = self.config.get_config(document_kind)

        return config.strategy

    def _has_basic_structure(self, text: str) -> bool:
        """
        Verifica se o texto tem estrutura básica para chunking estrutural.

        Critérios simples:
        - Tem parágrafos (para PARAGRAPH)
        - Tem pontuação de fim de sentença (para SENTENCE)
        """
        # Verifica se tem quebras de parágrafo
        has_paragraphs = bool(re.search(r'\n\s*\n', text))

        # Verifica se tem pontuação de fim de sentença
        has_sentences = bool(re.search(r'[.!?]', text))

        return has_paragraphs or has_sentences

    def _execute_chunking(
        self,
        text: str,
        strategy: ChunkingStrategy,
        config: AppChunkingConfig
    ) -> List[str]:
        """Executa a estratégia de chunking selecionada."""
        chunker = self.custom_chunker

        match strategy:
            case ChunkingStrategy.PARAGRAPH:
                return chunker.by_paragraph(text, config.chunk_size)

            case ChunkingStrategy.SENTENCE:
                return chunker.by_sentence(text, config.chunk_size, config.overlap)

            case ChunkingStrategy.SIZE:
                return chunker.by_size(text, config.chunk_size, config.overlap)

            case _:
                # Fallback para PARAGRAPH
                return chunker.by_paragraph(text, config.chunk_size)
