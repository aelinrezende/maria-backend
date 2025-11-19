"""DTOs para operações RAG (Retrieval-Augmented Generation)."""
from typing import List, Optional

from sqlmodel import Field, SQLModel

from backend.models.chunk import Chunk
from backend.modules.base.base_dto import BaseResponse, ModelBase
from backend.modules.document.document_enums import DocumentKind
from backend.modules.message.message_dto import ConversationPair
from backend.modules.message.message_enums import MessageRole
from backend.modules.rag.rag_enum import RAGChunkKind


class SourceInfo(BaseResponse):
    """Informações estruturadas de uma fonte utilizada no RAG."""
    order: int = Field()
    title: str = Field()
    source: str = Field()
    authors: List[str] = Field(default_factory=list)
    summary: str = Field()
    kind: DocumentKind = Field()
    url: Optional[str] = Field(default=None)
    date: Optional[str] = Field(default=None)


class MessageResponse(ModelBase):
    """DTO de resposta para Message."""

    content: str = Field()
    author_role: MessageRole = Field()
    sources: List[SourceInfo] = Field(default_factory=list)


class Conversation(BaseResponse):
    """Estrutura de conversa com mensagens do usuário e assistente."""
    user: MessageResponse
    assistant: MessageResponse


class RAGQueryRequest(SQLModel):
    """Payload para consulta RAG."""

    query: str = Field(
        min_length=1,
        max_length=1000,
        description="Pergunta do usuário"
    )


class RAGStreamChunk(ModelBase):
    """Chunk individual de streaming com metadados."""
    content: Optional[str] = Field(default=None)
    kind: RAGChunkKind = Field()
    sources: Optional[List[SourceInfo]] = Field(default=None)
    conversation: Optional[Conversation] = Field(default=None)

    @property
    def streamed(self) -> str:
        """Formata o chunk para streaming no formato SSE."""
        return f"data: {self.model_dump_json(exclude_none=True)}\n\n"

    @staticmethod
    def stream_content(content: str) -> str:
        """
        Retorna o chunk de conteúdo formatado para streaming no formato SSE.

        Args:
            content: Conteúdo gerado pelo LLM
        """
        return RAGStreamChunk(content=content, kind=RAGChunkKind.CONTENT).streamed

    @staticmethod
    def stream_source(sources: List[SourceInfo]) -> str:
        """
        Retorna o chunk de fontes formatado para streaming no formato SSE.

        Args:
            sources: Lista de informações das fontes utilizadas
        """
        return RAGStreamChunk(kind=RAGChunkKind.SOURCES, sources=sources).streamed

    @staticmethod
    def stream_final(messages: ConversationPair, sources: Optional[List[SourceInfo]] = None) -> str:
        """
        Retorna o chunk final formatado para streaming SSE.

        Args:
            messages: Tupla com mensagens do usuário e do assistente, respectivamente.
            sources: Lista de informações das fontes utilizadas
        """
        user_message, assistant_message = messages

        return RAGStreamChunk(
            kind=RAGChunkKind.FINAL,
            conversation=Conversation(
                user=user_message,
                assistant=MessageResponse(
                    **assistant_message.model_dump(), sources=sources or []
                )
            )
        ).streamed


class UserInputEvaluation(SQLModel):
    """Modelo para resposta de avaliação da entrada do usuário."""
    skip: bool


class SourceEvaluationResult(SQLModel):
    """Modelo para resposta de avaliação de fontes encontradas."""
    requires_new_query: bool
    irrelevant_chunks_zero_based_indexes: List[int] = []

    @staticmethod
    def empty() -> "SourceEvaluationResult":
        """Retorna um resultado vazio padrão."""
        return SourceEvaluationResult(
            requires_new_query=False,
            irrelevant_chunks_zero_based_indexes=[]
        )


class QueryExpansionResponse(SQLModel):
    """Modelo para resposta de expansão e extração de consultas."""
    improved_input: str = Field(
        description="Consulta reformulada e expandida para melhor precisão na busca"
    )
    entities_and_keywords: List[str] = Field(
        description="Lista de entidades e palavras-chave extraídas da consulta"
    )

    @staticmethod
    def fallback(original_query: str) -> "QueryExpansionResponse":
        """Retorna uma resposta de fallback usando a query original."""
        return QueryExpansionResponse(
            improved_input=original_query,
            entities_and_keywords=[]
        )


class ChunkRefinementResponse(SQLModel):
    """Modelo para resposta de refinamento e reordenação de chunks."""
    refined_text: str = Field(
        min_length=1,
        description="Texto refinado e reestruturado dos chunks originais"
    )

    @staticmethod
    def fallback(chunks: List[Chunk]) -> "ChunkRefinementResponse":
        """Retorna uma resposta de fallback usando o texto original concatenado."""
        return ChunkRefinementResponse(
            refined_text="\n\n".join([chunk.content for chunk in chunks])
        )
