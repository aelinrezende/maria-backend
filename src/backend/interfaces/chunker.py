from typing import Protocol


class IChunker(Protocol):
    """Contrato mínimo para serviços de chunking de texto.

    Define o método assíncrono `chunk` que recebe um texto e retorna uma
    lista de strings (chunks).
    """

    def by_paragraph(self, text: str) -> list[str]:
        """Divide o texto em chunks por parágrafos."""

    def by_sentence(self, text: str) -> list[str]:
        """Divide o texto em chunks por sentenças."""
