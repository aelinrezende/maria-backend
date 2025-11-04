"""
DTOs para o sistema de migrações automáticas
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict


class MigrationResult(BaseModel):
    """Resultado da execução de uma migration"""
    model_config = ConfigDict(from_attributes=True)

    success: bool
    message: str
    applied_count: int = 0
    pending_count: int = 0
    current_revision: Optional[str] = None
    target_revision: Optional[str] = None
    duration_seconds: float = 0.0
    error_details: Optional[str] = None
