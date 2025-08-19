"""Módulo para processamento e divisão de texto (chunking).

Responsabilidades:
- Implementar diferentes estratégias de chunking (parágrafo, sentença, etc.).
- Orquestrar a seleção da estratégia correta com base no tipo de conteúdo.
- Normalizar e limpar o texto antes do chunking.
"""
from __future__ import annotations

import re
from typing import List


def chunk_by_paragraph(text: str) -> List[str]:
    """Divide um texto em parágrafos.

    A função considera um parágrafo como um bloco de texto separado
    por uma ou mais linhas em branco. Também remove parágrafos vazios
    resultantes da divisão.

    Args:
        text: O texto em formato Markdown a ser dividido.

    Returns:
        Uma lista de strings, onde cada string é um parágrafo.
    """
    if not text:
        return []

    paragraphs = re.split(r'\n\s*\n', text.strip())

    return [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]
