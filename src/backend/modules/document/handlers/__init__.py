"""
Handlers para processamento de documentos via LLM
"""
from backend.modules.document.handlers.ingest_ai_file import ingest_file_by_ai
from backend.modules.document.handlers.ingest_file import ingest_file

__all__ = ["ingest_file_by_ai", "ingest_file"]
