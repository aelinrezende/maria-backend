"""Router para endpoints RAG (Retrieval-Augmented Generation)."""


from fastapi import Depends
from fastapi.responses import StreamingResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from wireup import service as inject

from backend.cross_cutting.middleware.auth import authenticate
from backend.cross_cutting.middleware.chat.chat import load_user_messages

from .rag_dto import RAGQueryRequest
from .rag_hub import RAGHub

rag_router = InferringRouter(prefix="/rag", tags=["RAG"])


@inject(lifetime="scoped")
@cbv(rag_router)
class RAGRouter:
    """Endpoints para consultas RAG."""

    def __init__(self, hub: RAGHub = Depends()):
        self.hub = hub

    @rag_router.post(
        "/query/stream",
        summary="Consultas RAG com streaming de respostas"
    )
    async def query_rag_stream(
        self,
        request: RAGQueryRequest,
        _=Depends(authenticate),
        __=Depends(load_user_messages)
    ) -> StreamingResponse:
        """
        Endpoint para consultas RAG com streaming de respostas.

        Args:
            request: Requisição com query

        Returns:
            Streaming da resposta gerada em tempo real
        """
        return StreamingResponse(
            self.hub.query_rag_stream(request),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
                "Access-Control-Allow-Origin": "*"
            }
        )
