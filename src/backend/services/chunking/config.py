"""Configurações específicas para cada área de foco do Mar.IA."""
from dataclasses import dataclass
from typing import Dict

from backend.modules.document.document_enums import DocumentKind
from backend.services.chunking.enums import ChunkingStrategy


@dataclass
class ChunkingConfig:
    """Configuração para uma estratégia específica de chunking."""

    strategy: ChunkingStrategy
    chunk_size: int
    overlap: int


class AppChunkingConfig:
    """Configurações de chunking específicas para as áreas de foco do Mar.IA."""

    def __init__(self):
        """Inicializa as configurações por área de foco."""
        # Configurações por área de foco
        self.configs: Dict[DocumentKind, ChunkingConfig] = {

            # Área 1: Riscos e Caminhos Seguros - Automedicação Hormonal
            DocumentKind.HORMONAL_SAFETY: ChunkingConfig(
                strategy=ChunkingStrategy.SENTENCE,
                chunk_size=300,  # Chunks menores para precisão médica
                overlap=40       # Overlap maior para contexto de segurança
            ),

            # Área 2: Retificação de Nome e Gênero em Documentos
            DocumentKind.LEGAL_PROCEDURES: ChunkingConfig(
                strategy=ChunkingStrategy.SENTENCE,
                chunk_size=400,  # Detalhes legais precisos
                overlap=30       # Overlap moderado para contexto legal
            ),

            # Área 3: Cirurgias de Afirmação de Gênero via Planos de Saúde
            DocumentKind.HEALTH_INSURANCE: ChunkingConfig(
                strategy=ChunkingStrategy.PARAGRAPH,
                chunk_size=500,  # Chunks maiores para procedimentos completos
                overlap=50       # Overlap maior para manter contexto de direitos
            )
        }

    def get_config(self, document_kind: DocumentKind) -> ChunkingConfig:
        """Retorna a configuração para um tipo específico de documento."""
        return self.configs.get(document_kind, self._get_default_config())

    def _get_default_config(self) -> ChunkingConfig:
        """Configuração padrão para casos não mapeados."""
        return ChunkingConfig(
            strategy=ChunkingStrategy.PARAGRAPH,
            chunk_size=400,
            overlap=30
        )
