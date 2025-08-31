"""Utilitários para operações comuns de chunking.

Módulo com funções auxiliares reutilizáveis para diferentes estratégias de chunking.
Centraliza lógicas comuns como limpeza de texto e algoritmos de agrupamento.
"""
from __future__ import annotations

import re
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
    def clean_deep(parts: List[str]) -> List[str]:
        """Limpa e normaliza uma lista de partes de texto.

        Remove espaços em branco extras, filtra partes vazias e
        normaliza quebras de linha internas para espaços simples.

        Args:
            parts: Lista de strings a serem limpas e normalizadas

        Returns:
            Lista de strings limpas, não vazias e normalizadas
        """
        return [
            re.sub(r'\n+', ' ', part.strip())
            for part in parts
            if part.strip()
        ]

    @staticmethod
    def chunk_by_size_fallback(
        text: str,
        chunk_size: int,
        overlap: int,
    ) -> List[str]:
        """Fallback para dividir textos muito grandes usando janela deslizante.

        Utiliza uma estratégia de janela deslizante (sliding window) para dividir
        textos que excedem o chunk_size. Mantém overlap entre chunks para preservar
        contexto nas bordas.

        Args:
            text: Texto a ser dividido
            chunk_size: Tamanho máximo de cada chunk em caracteres
            overlap: Número de caracteres para sobrepor entre chunks adjacentes

        Returns:
            Lista de chunks com tamanho controlado e overlap preservado
        """
        if len(text) <= chunk_size:
            return [text] if text.strip() else []

        chunks: List[str] = []
        start: int = 0

        while start < len(text):
            # Define fim do chunk atual
            end = start + chunk_size

            # Se é o último chunk, pega até o final
            if end >= len(text):
                chunk = text[start:].strip()

                if chunk:
                    chunks.append(chunk)

                break

            best_break, last_step = end, max(end // 2, end - 100)

            # Procura por um espaço próximo ao fim para não quebrar palavras
            for i in range(end, last_step, -1):
                if text[i].isspace():
                    best_break = i

                    break

            chunk = text[start:best_break].strip()

            if chunk:
                chunks.append(chunk)

            # Move o início para o próximo chunk, considerando o overlap e garantindo avanço
            start = max(start + 1, best_break - overlap)

        return chunks

    @staticmethod
    def greedy_merge_chunks(
        parts: List[str],
        chunk_size: int,
        overlap: int,
        joiner: str,
    ) -> List[str]:
        """Algoritmo comum de Greedy Merging para qualquer tipo de unidade.

        Agrupa partes consecutivas (parágrafos, sentenças, etc.) para formar
        chunks que se aproximem do chunk_size sem ultrapassá-lo. Aplica fallback
        automático para partes que excedem o tamanho limite.

        Args:
            parts: Lista de partes a serem agrupadas (parágrafos, sentenças, etc.)
            chunk_size: Tamanho máximo aproximado de cada chunk em caracteres
            overlap: Número de caracteres para sobrepor entre chunks adjacentes
            joiner: String usada para unir as partes (ex: "\\n\\n" para parágrafos, " " para sentenças)

        Returns:
            Lista de chunks otimizados com fallback aplicado
        """
        merged_chunks: List[str] = []
        current_chunk_parts: List[str] = []
        current_chunk_size = 0

        def merge_chunks():
            merged_chunks.append(
                joiner.join(current_chunk_parts)
            )

        for part in parts:
            part_size = len(part)

            # Aplica fallback se a parte sozinha já excede o chunk_size
            if part_size > chunk_size:
                # Finaliza chunk atual se existir
                if current_chunk_parts:
                    merge_chunks()
                    current_chunk_parts, current_chunk_size = [], 0

                # Aplica fallback por tamanho na parte muito grande
                fallback_chunks = ChunkingUtils.chunk_by_size_fallback(
                    part, chunk_size, overlap
                )

                merged_chunks.extend(fallback_chunks)

                continue

            # Aproximação simples: soma o tamanho das partes + estimativa de separadores
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
                merge_chunks()

            current_chunk_parts, current_chunk_size = [part], part_size

        # Adiciona o último chunk que estava sendo montado
        if current_chunk_parts:
            merge_chunks()

        return merged_chunks
