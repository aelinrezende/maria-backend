"""Utilitários para operações comuns de chunking.

Módulo com funções auxiliares reutilizáveis para diferentes estratégias de chunking.
Centraliza lógicas comuns como limpeza de texto e algoritmos de agrupamento.
"""
from __future__ import annotations

from typing import List


class ChunkingUtils:
    """Classe utilitária com métodos estáticos para operações comuns de chunking."""

    @staticmethod
    def clean(parts: List[str]) -> List[str]:
        """Limpa e filtra uma lista de partes de texto.

        Remove espaços em branco extras e filtra partes vazias.
        Centraliza a lógica de limpeza usada em múltiplas estratégias.

        Args:
            parts: Lista de strings a serem limpas

        Returns:
            Lista de strings limpas e não vazias
        """
        return [
            part.strip()
            for part in parts
            if part.strip()
        ]

    @staticmethod
    def greedy_merge_chunks(
        parts: List[str],
        chunk_size: int,
        joiner: str,
    ) -> List[str]:
        """Algoritmo comum de Greedy Merging para qualquer tipo de unidade.

        Agrupa partes consecutivas (parágrafos, sentenças, etc.) para formar
        chunks que se aproximem do chunk_size sem ultrapassá-lo.

        Args:
            parts: Lista de partes a serem agrupadas (parágrafos, sentenças, etc.)
            chunk_size: Tamanho máximo aproximado de cada chunk em caracteres
            joiner: String usada para unir as partes (ex: "\\n\\n" para parágrafos, " " para sentenças)

        Returns:
            Lista de chunks otimizados
        """
        merged_chunks: List[str] = []
        current_chunk_parts: List[str] = []
        current_chunk_size = 0

        for part in parts:
            # TODO: Implementar fallback para partes que sozinhas já excedem o chunk_size.
            # Atualmente, elas serão adicionadas como um chunk individual muito grande.

            # Aproximação simples: soma o tamanho das partes + estimativa de separadores
            part_size = len(part)
            partial_size = (
                current_chunk_size +
                part_size + max(0, len(current_chunk_parts) - 1)
            )

            # Caso a parte atual esteja abaixo do limite,
            # ela é adicionada ao chunk atual para reutilização
            if partial_size <= chunk_size or not current_chunk_parts:
                current_chunk_parts.append(part)
                current_chunk_size += part_size

                continue

            if current_chunk_parts:
                merged_chunks.append(joiner.join(current_chunk_parts))

            current_chunk_parts, current_chunk_size = [part], part_size

        # Adiciona o último chunk que estava sendo montado
        if current_chunk_parts:
            merged_chunks.append(joiner.join(current_chunk_parts))

        return merged_chunks
