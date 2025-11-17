"""
Handler para obtenção de perfil de usuário.

Implementa a lógica para retornar dados do perfil do usuário autenticado,
garantindo que apenas usuários ativos possam acessar suas próprias informações.
"""


from backend.exceptions.http_exceptions import UnauthorizedException
from backend.models.user import User
from backend.modules.user.user_dto import UserResponse
from backend.modules.user.user_enums import UserStatus


def get_profile(
    current_user: User,
) -> UserResponse:
    """
    Obtém dados do perfil do usuário autenticado.

    Args:
        current_user: Usuário autenticado

    Returns:
        UserResponse: Dados do perfil do usuário

    Raises:
        UnauthorizedException: Se usuário não estiver ativo
    """
    if current_user.status != UserStatus.ACTIVE:
        raise UnauthorizedException("USER_INACTIVE")

    return current_user
