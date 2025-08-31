"""Módulo com funções de conversão de formatos.

Responsabilidades:
- Converter HTML para Markdown.
"""
from __future__ import annotations

from markdownify import markdownify as md


def html_to_markdown(html_content: str) -> str:
    """Converte uma string de conteúdo HTML para Markdown.

    Utiliza a biblioteca `markdownify` para uma conversão robusta,
    preservando a semântica de títulos, listas e parágrafos.

    Args:
        html_content: A string contendo o HTML a ser convertido.

    Returns:
        Uma string contendo o texto em formato Markdown.
    """
    if not isinstance(html_content, str) or html_content.strip() == '':
        return ""

    # A função md() da biblioteca markdownify faz a conversão.
    # heading_style="ATX": usar ## em vez de ---- para títulos (melhor para embeddings)
    return md(html_content, heading_style="ATX").strip()
