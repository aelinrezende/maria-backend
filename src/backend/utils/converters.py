"""Módulo com funções de conversão de formatos.

Responsabilidades:
- Converter HTML para Markdown.
"""
from __future__ import annotations

from io import BytesIO

from fastapi import UploadFile
from markitdown import MarkItDown

from backend.exceptions.http_exceptions import BadRequestException

md = MarkItDown()


def document_to_markdown(document_file: UploadFile) -> str:
    """Converte um documento/arquivo para Markdown.

    Utiliza a biblioteca `markitdown` para uma conversão robusta,
    preservando a semântica e suportando múltiplos formatos.

    Args:
        document_file: Um arquivo contendo o conteúdo do documento (HTML, DOCX, PDF, etc.)

    Returns:
        Uma string contendo o texto em formato Markdown.

    Raises:
        BadRequestException: Se a conversão falhar por qualquer motivo.
    """
    try:
        # Reset do ponteiro para o início
        document_file.file.seek(0)

        # Lê todo o conteúdo em memória
        clean_stream = BytesIO(document_file.file.read())

        # MarkItDown converte usando o stream limpo
        result = md.convert_stream(clean_stream)

        # Reset do arquivo original para outras operações se necessário
        document_file.file.seek(0)

        return result.text_content.strip()

    except Exception as exception:
        raise BadRequestException("FAILED_TO_CONVERT_DOCUMENT") from exception
