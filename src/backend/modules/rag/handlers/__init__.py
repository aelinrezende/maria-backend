""" Handlers para o módulo RAG."""

from backend.modules.rag.handlers.direct_response import generate_direct_response
from backend.modules.rag.handlers.evaluate_user_query import should_skip_rag

__all__ = [
    "should_skip_rag",
    "generate_direct_response"
]
