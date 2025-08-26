"""Módulo para processamento e divisão de texto (chunking).

Responsabilidades:
- Implementar diferentes estratégias de chunking (parágrafo, sentença, etc.).
- Orquestrar a seleção da estratégia correta com base no tipo de conteúdo.
- Normalizar e limpar o texto antes do chunking.
"""
from __future__ import annotations

import re
from typing import List

from backend.core.config import settings


def chunk_by_paragraph(
    text: str,
    chunk_size: int = settings.CHUNK_SIZE,
) -> List[str]:
    """Divide um texto em parágrafos, agrupando os menores (Greedy Merging).

    A função primeiro divide o texto em parágrafos. Em seguida, agrupa
    parágrafos consecutivos para formar chunks que se aproximem do `chunk_size`
    sem ultrapassá-lo.

    Args:
        text: O texto em formato Markdown a ser dividido.
        chunk_size: O tamanho máximo aproximado de cada chunk em caracteres.

    Returns:
        Uma lista de strings, onde cada string é um chunk otimizado.
    """
    if not text:
        return []

    # 1. Divide o texto em parágrafos iniciais
    initial_paragraphs = re.split(r'\n\s*\n', text.strip())

    cleaned_paragraphs = [
        paragraph.strip()
        for paragraph in initial_paragraphs if paragraph.strip()
    ]

    if not cleaned_paragraphs:
        return []

    # 2. Agrupa parágrafos para formar chunks (Greedy Merging)
    merged_chunks: List[str] = []
    current_chunk_parts: List[str] = []
    current_chunk_size = 0

    for paragraph in cleaned_paragraphs:
        # TODO: Implementar fallback para parágrafos que sozinhos já excedem o chunk_size.
        # Atualmente, eles serão adicionados como um chunk individual muito grande.

        paragraph_size = len(paragraph)
        partial_size = (
            current_chunk_size + paragraph_size + len(current_chunk_parts)
        )

        # Caso o parágrafo atual esteja abaixo do limite,
        # ele é adicionado ao chunk atual para reutilização
        if partial_size <= chunk_size and current_chunk_parts:
            current_chunk_parts.append(paragraph)
            current_chunk_size += paragraph_size

            continue

        merged_chunks.append(_as_chunk(current_chunk_parts))
        current_chunk_parts, current_chunk_size = [paragraph], paragraph_size

    # Adiciona o último chunk que estava sendo montado
    if current_chunk_parts:
        merged_chunks.append(_as_chunk(current_chunk_parts))

    return merged_chunks


def _as_chunk(chunks: List[str]) -> str:
    """Converte uma lista de strings em um único chunk formatado."""
    return "\n\n".join(chunks)
