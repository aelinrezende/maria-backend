"""Router para endpoints RAG (Retrieval-Augmented Generation)."""

from fastapi import Depends
from fastapi.responses import StreamingResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from wireup import service as inject

from backend.cross_cutting.middleware.auth.auth import authenticate

from .rag_dto import RAGQueryRequest
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
        summary="Consultas RAG com streaming de respostas"
    )
    async def query_rag_stream(
        self,
        request: RAGQueryRequest,
        _=Depends(authenticate),
    ) -> StreamingResponse:
        """
        Endpoint para consultas RAG com streaming de respostas.

        Args:
            request: Requisição com query

        Returns:
            Streaming da resposta gerada em tempo real
        """
        return StreamingResponse(
            self.service.query_rag_stream(request),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
                "Access-Control-Allow-Origin": "*"
            }
        )
