from typing import Protocol


class IChunker(Protocol):
    """Contrato mínimo para serviços de chunking de texto.

    Define os métodos para diferentes estratégias de chunking:
    - by_paragraph: Chunking por parágrafos
    - by_sentence: Chunking por sentenças
    - by_size: Chunking por tamanho (fallback)
    """

    def by_paragraph(self, text: str) -> list[str]:
        """Divide o texto em chunks por parágrafos."""

    def by_sentence(self, text: str) -> list[str]:
        """Divide o texto em chunks por sentenças."""

    def by_size(self, text: str, chunk_size: int, overlap: int = 50) -> list[str]:
        """Divide o texto em chunks por tamanho usando janela deslizante."""
