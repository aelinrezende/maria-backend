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
    pages: List[PaperPage] = []
    title: Optional[str] = None
    metadata: dict = {}

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
        """Extrai páginas de PDF usando pdfplumber."""

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
