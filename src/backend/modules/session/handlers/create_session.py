"""
Handler para criação de sessões de usuário.
"""

from typing import TYPE_CHECKING

from backend.models.session import Session
from backend.modules.session.session_dto import SessionResponse
from backend.modules.session.session_enums import SessionStatus

if TYPE_CHECKING:
    from backend.modules.session.session_service import SessionService


async def create_user_session(
    session_service: "SessionService",
    user_id: str,
    token: str
) -> SessionResponse:
    """
    Cria uma nova sessão para o usuário.

    Args:
        session_service: Instância do SessionService
        user_id: ID do usuário
        token: Token JWT gerado

    Returns:
        SessionResponse: Dados da sessão criada
    """
    session = Session(
        user_id=user_id,
        token=token,
        status=SessionStatus.ACTIVE
    )

    created_session = await session_service.create(session.model_dump())

    return SessionResponse(**created_session.model_dump())
