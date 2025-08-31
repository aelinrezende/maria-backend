
"""Módulo que implementa um chunker personalizado para dividir textos em chunks otimizados."""

import re
from typing import List

from backend.core.config import settings
from backend.interfaces.chunker import IChunker

from .utils import ChunkingUtils


class CustomChunker(IChunker):
    """Implementação personalizada do serviço de chunking.

    Esta classe implementa o contrato definido por IChunker, utilizando
    estratégias específicas para dividir textos em chunks por parágrafos
    e por sentenças.
    """

    def by_paragraph(
        self,
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

        # 2. Limpa e filtra parágrafos usando utilitário
        cleaned_paragraphs = ChunkingUtils.clean(initial_paragraphs)

        if not cleaned_paragraphs:
            return []

        # 3. Usa o algoritmo comum de Greedy Merging
        return ChunkingUtils.greedy_merge_chunks(
            parts=cleaned_paragraphs,
            chunk_size=chunk_size,
            overlap=settings.CHUNK_OVERLAP,
            joiner="\n\n",
        )

    def by_sentence(
        self,
        text: str,
        chunk_size: int = settings.CHUNK_SIZE,
        overlap: int = settings.CHUNK_OVERLAP,
    ) -> List[str]:
        """Divide um texto em sentenças, agrupando as menores (Greedy Merging).

        Estratégia específica para documentos legais onde a preservação da
        granularidade de sentenças é crítica. Aplica o mesmo algoritmo de
        "Greedy Merging" do chunking por parágrafo, mas usando sentenças
        como unidade base.

        Args:
            text: O texto em formato Markdown a ser dividido.
            chunk_size: O tamanho máximo aproximado de cada chunk em caracteres.
            overlap: Número de caracteres para sobrepor entre chunks adjacentes

        Returns:
            Uma lista de strings, onde cada string é um chunk otimizado
            preservando a integridade das sentenças.
        """
        if not text:
            return []

        # Regex para dividir sentenças por pontuação de fim
        # (?<!\n\d)   : Evita dividir após quebras de linha seguidas de dígito (ex: listas numeradas como "1. Item")
        # [.!?]+      : Captura um ou mais sinais de pontuação de fim de sentença
        # (?:\s+(?=[A-Z])|$) : Garante que a divisão ocorra apenas se houver espaço seguido de letra maiúscula (nova sentença) ou fim de string
        # Isso evita dividir sentenças em listas numeradas e preserva a integridade das sentenças.
        sentence_pattern = r'(?<!\n\d)[.!?]+(?:\s+(?=[A-Z])|$)'

        # 1. Aplica regex ANTES da normalização (preserva contexto de quebras de linha)
        raw_sentences = re.split(sentence_pattern, text.strip())

        # 2. Normaliza e limpa sentenças vazias
        sentences = ChunkingUtils.clean_deep(raw_sentences)

        if not sentences:
            return []

        # 3. Usa o algoritmo comum de Greedy Merging
        return ChunkingUtils.greedy_merge_chunks(
            parts=sentences,
            chunk_size=chunk_size,
            overlap=overlap,
            joiner=" ",
        )

    def by_size(
        self,
        text: str,
        chunk_size: int = settings.CHUNK_SIZE,
        overlap: int = settings.CHUNK_OVERLAP,
    ) -> List[str]:
        """Divide um texto em chunks por tamanho usando janela deslizante.

        Estratégia de fallback para textos muito grandes que não podem ser
        divididos adequadamente por estrutura (parágrafos/sentenças).
        Utiliza janela deslizante com overlap para preservar contexto.

        Args:
            text: O texto a ser dividido.
            chunk_size: O tamanho máximo de cada chunk em caracteres.
            overlap: Número de caracteres para sobrepor entre chunks.

        Returns:
            Uma lista de strings com tamanho controlado e overlap.
        """
        return ChunkingUtils.chunk_by_size_fallback(text, chunk_size, overlap)
