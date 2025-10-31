"""
Handler para validação de código de convite.

Implementa a lógica completa de validação de códigos de convite,
incluindo verificação de existência, expiração e status do usuário.
"""

from typing import TYPE_CHECKING

from backend.exceptions.http_exceptions import (
    BadRequestException,
    NotFoundException,
)
from backend.modules.user.user_dto import UserResponse
from backend.modules.user.user_enums import UserStatus
from backend.utils import date

if TYPE_CHECKING:
    from backend.modules.user.user_service import UserService


async def validate_invitation(
    user_service: "UserService",
    invitation_code: str
) -> UserResponse:
    """
    Valida um código de convite verificando existência, expiração e status.

    Args:
        user_service: Instância do UserService
        invitation_code: Código de convite a ser validado

    Returns:
        UserResponse: Dados do usuário se código for válido

    Raises:
        BadRequestException: Se o código estiver expirado ou já foi usado
        NotFoundException: Se o código não for encontrado
    """
    # Busca usuário pelo código de convite
    user = await user_service.repository.find_by_invitation_code(invitation_code)

    if not user or not user.invitation_code:
        raise NotFoundException("CODE_NOT_FOUND")

    expiration_date = user.invitation_code_expiration_date

    # Verifica se o código está expirado
    if expiration_date and date.is_past(expiration_date):
        raise BadRequestException("CODE_EXPIRED")

    # Verifica se usuário ainda tem status INVITED
    if user.status != UserStatus.INVITED:
        raise BadRequestException("CODE_ALREADY_USED")

    return UserResponse(**user.model_dump())
