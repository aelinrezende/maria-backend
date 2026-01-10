"""Handler para paginação de mensagens do usuário."""

from typing import TYPE_CHECKING, Optional

from backend.cross_cutting.middleware.auth import get_requesting_user
from backend.modules.base.base_dto import PaginatedResponse, PaginateRequest

if TYPE_CHECKING:
    from backend.modules.message.message_hub import MessageHub


async def paginate_user_messages(
    hub: "MessageHub",
    request: Optional[PaginateRequest] = None,
) -> PaginatedResponse:
    """
    Processa requisição de paginação de mensagens.

    Args:
        hub: Instância do MessageHub
        request: Parâmetros de paginação

    Returns:
        Resposta paginada com mensagens do usuário
    """
    requesting_user = get_requesting_user()

    return await hub.repository.get_cursor_paginated_messages(
        user_id=requesting_user.id,
        request=request or PaginateRequest()
    )
