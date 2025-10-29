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
        BadRequestException: Se formato do código for inválido
        NotFoundException: Se código não for encontrado
        ConflictException: Se código já foi utilizado ou expirou
    """
    # Busca usuário pelo código de convite
    user = await user_service.repository.find_by_invitation_code(invitation_code)

    if not user or not user.invitation_code:
        raise NotFoundException("CODE_NOT_FOUND")

    # Verifica se o código está expirado
    if date.is_past(user.invitation_code_expiration_date):
        raise BadRequestException("CODE_EXPIRED")

    # Verifica se usuário ainda tem status INVITED
    if user.status != UserStatus.INVITED:
        raise BadRequestException("CODE_ALREADY_USED")

    return UserResponse(**user.model_dump())
