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
from backend.services.chunking.models import PaperChunk
from backend.services.converter.models import PaperPage


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
        papers_pages: List[PaperPage],
        document_kind: DocumentKind,
        force_strategy: Optional[ChunkingStrategy] = None
    ) -> List[PaperChunk]:
        """
        Executa chunking inteligente para as áreas do Mar.IA.

        Estratégia por área:
        - HORMONAL_SAFETY: SENTENCE (precisão médica)
        - LEGAL_PROCEDURES: SENTENCE (precisão legal)  
        - HEALTH_INSURANCE: PARAGRAPH (contexto de procedimentos)
        """
        if not papers_pages:
            return []

        # 1. Seleciona estratégia
        strategy = force_strategy or self._select_strategy(
            papers_pages, document_kind
        )

        # 2. Obtém configuração específica
        config = self.config.get_config(document_kind)

        # 3. Executa chunking
        chunks = self._execute_chunking(papers_pages, strategy, config)

        # 4. Retorna resultado
        return chunks

    def _select_strategy(
        self,
        papers_pages: List[PaperPage],
        document_kind: DocumentKind
    ) -> ChunkingStrategy:
        """Seleciona a estratégia de chunking mais apropriada."""

        # Verifica se o texto tem estrutura formal mínima
        if not self._has_basic_structure(papers_pages):
            return ChunkingStrategy.SIZE

        # Estratégia baseada na configuração por área
        config = self.config.get_config(document_kind)

        return config.strategy

    def _has_basic_structure(self, papers_pages: List[PaperPage]) -> bool:
        """
        Verifica se o texto tem estrutura básica para chunking estrutural.

        Critérios simples:
        - Tem parágrafos (para PARAGRAPH)
        - Tem pontuação de fim de sentença (para SENTENCE)
        """
        # Analisa apenas as primeiras 3 páginas
        first_pages = papers_pages[:3]

        text = "\n\n".join(
            page.content for page in first_pages if page.content.strip()
        )

        # Verifica se tem quebras de parágrafo
        has_paragraphs = bool(re.search(r'\n\s*\n', text))

        # Verifica se tem pontuação de fim de sentença
        has_sentences = bool(re.search(r'[.!?]', text))

        return has_paragraphs or has_sentences

    def _execute_chunking(
        self,
        papers_pages: List[PaperPage],
        strategy: ChunkingStrategy,
        config: AppChunkingConfig
    ) -> List[PaperChunk]:
        """Executa a estratégia de chunking selecionada."""
        chunker = self.custom_chunker
        chunked_pages: List[PaperChunk] = []

        for paper in papers_pages:
            text = paper.content
            chunks: List[str] = []

            match strategy:
                case ChunkingStrategy.PARAGRAPH:
                    chunks = chunker.by_paragraph(text, config.chunk_size)

                case ChunkingStrategy.SENTENCE:
                    chunks = chunker.by_sentence(
                        text, config.chunk_size, config.overlap
                    )

                case ChunkingStrategy.SIZE:
                    chunks = chunker.by_size(
                        text, config.chunk_size, config.overlap
                    )

                case _:
                    # Fallback para PARAGRAPH
                    chunks = chunker.by_paragraph(text, config.chunk_size)

            chunked_pages.extend(PaperChunk(
                page=paper.page,
                content=chunk
            ) for chunk in chunks)

        return chunked_pages
