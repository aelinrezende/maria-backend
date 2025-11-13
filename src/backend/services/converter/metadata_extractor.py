"""
Extrai texto de documentos e metadados de PDFs
"""

from typing import Any, BinaryIO, List, Optional

import pymupdf
import pymupdf4llm
from markitdown import MarkItDown
from markitdown._base_converter import DocumentConverter, DocumentConverterResult
from markitdown._stream_info import StreamInfo

from backend.services.converter.models import PaperPage

_md = MarkItDown()


class MetadataExtractor(DocumentConverter):
    """
    Extrai texto e metadados de documentos.
    """

    def __init__(self):
        super().__init__()
        self.pages: List[PaperPage] = []
        self.title: Optional[str] = None
        self.metadata: Optional[dict[str, Any]] = None

    def accepts(self, _file_stream: BinaryIO, _stream_info: StreamInfo, **_kwargs: Any) -> bool:
        """Aceita todos os formatos de arquivo."""
        return True

    def convert(self, file_stream: BinaryIO, stream_info: StreamInfo, **_kwargs: Any) -> DocumentConverterResult:
        """Converte documento extraindo texto com informações de página."""
        extension = (stream_info.extension or "").lower()

        # Extrai metadados do PDF
        if extension == '.pdf':
            self._extract_pdf_pages(file_stream)

        # Fallback para outros formatos
        else:
            self.pages.append(PaperPage(
                page=1,
                content=_md.convert_stream(
                    file_stream, stream_info=stream_info
                ).markdown
            ))

        return DocumentConverterResult(
            markdown="DO NOT USE",
        )

    def _extract_pdf_pages(self, file_stream: BinaryIO):
        """Extrai páginas de PDF usando pymupdf."""

        with pymupdf.open(stream=file_stream) as pdf:
            # pylint: disable=no-member
            self.title, self.metadata = pdf.metadata.get("title"), pdf.metadata

            for page, _ in enumerate(pdf):
                text = pymupdf4llm.to_markdown(pdf, pages=[page]).strip()

                if text:
                    self.pages.append(PaperPage(
                        page=page + 1,
                        content=text
                    ))


def extract_initial_pages(pages: List[PaperPage], max_pages: int = 3, max_chars: int = 8000) -> str:
    """
    Extrai conteúdo das primeiras páginas com limite simples de caracteres.

    Args:
        pages: Lista de páginas do documento
        max_pages: Número máximo de páginas a extrair (padrão: 3)
        max_chars: Número máximo de caracteres totais (padrão: 8000)

    Returns:
        str: Conteúdo concatenado das primeiras páginas dentro dos limites
    """
    selected_pages = pages[:max_pages]
    content_parts = []
    total_chars = 0

    for page in selected_pages:
        page_content = page.content.strip()
        content_length = len(page_content)

        if not page_content:
            continue

        if total_chars + content_length > max_chars:
            remaining_chars = max_chars - total_chars

            if remaining_chars > 0:
                content_parts.append(
                    page_content[:remaining_chars] + "..."
                )

            break

        content_parts.append(page_content)
        total_chars += content_length

    return "\n\n--- PÁGINA SEPARADORA ---\n\n".join(content_parts)
