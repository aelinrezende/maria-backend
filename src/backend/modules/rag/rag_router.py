"""Router para endpoints RAG (Retrieval-Augmented Generation)."""

from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from wireup import service as inject

from .rag_dto import RAGQueryRequest, RAGQueryResponse
from .rag_service import RAGService

rag_router = InferringRouter(prefix="/rag", tags=["RAG"])


@inject(lifetime="scoped")
@cbv(rag_router)
class RAGRouter:
    """Endpoints para consultas RAG."""

    def __init__(self, service: RAGService = Depends()):
        self.service = service

    @rag_router.post(
        "/query/stream",
        response_model=RAGQueryResponse,
        summary="Consultas RAG com streaming de respostas"
    )
    async def query_rag_stream(
        self,
        request: RAGQueryRequest,
    ) -> RAGQueryResponse:
        """
        Endpoint para consultas RAG com streaming de respostas.

        Args:
            request: Requisição com query

        Returns:
            Streaming da resposta gerada
        """
        return await self.service.query_rag_stream(request)
