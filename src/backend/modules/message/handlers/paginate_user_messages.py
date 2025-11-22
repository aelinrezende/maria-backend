"""Handler para paginação de mensagens do usuário."""

from typing import Optional

from backend.cross_cutting.middleware.auth import get_requesting_user
from backend.modules.base.base_dto import PaginatedResponse, PaginateRequest
from backend.modules.message.message_service import MessageService


async def paginate_user_messages(
    hub: MessageService,
    request: Optional[PaginateRequest] = None,
) -> PaginatedResponse:
    """
    Processa requisição de paginação de mensagens.

    Args:
        hub: Instância do MessageService
        request: Parâmetros de paginação

    Returns:
        Resposta paginada com mensagens do usuário
    """
    requesting_user = get_requesting_user()

    return await hub.repository.get_cursor_paginated_messages(
        user_id=requesting_user.id,
        request=request or PaginateRequest()
    )
