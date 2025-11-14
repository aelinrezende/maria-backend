"""
Handler para login de usuário.

Implementa a lógica completa de autenticação, incluindo
validação de credenciais, verificação de bcrypt e geração de tokens JWT.
"""

from typing import TYPE_CHECKING

from backend.exceptions.http_exceptions import UnauthorizedException
from backend.models.session import Session
from backend.modules.auth.auth_dto import LoginRequest
from backend.modules.session.session_enums import SessionStatus
from backend.modules.user.user_enums import UserStatus
from backend.utils.jwt import create_user_token
from backend.utils.password import verify_password

if TYPE_CHECKING:
    from backend.modules.user.user_service import UserService


async def login(
    hub: "UserService",
    request: LoginRequest,
) -> Session:
    """
    Autentica usuário e cria sessão.

    Args:
        hub: UserService para acesso a repositórios e métodos
        request: Dados de login (email e senha)

    Returns:
        Session: Dados da sessão criada com token JWT
    Raises:
        UnauthorizedException: Credenciais inválidas ou usuário inativo
    """
    user = await hub.repository.find_by_email(request.email)

    if not user:
        raise UnauthorizedException("INVALID_CREDENTIALS")

    if user.status != UserStatus.ACTIVE:
        raise UnauthorizedException("INVALID_CREDENTIALS")

    if not user.password or not verify_password(request.password, user.password):
        raise UnauthorizedException("INVALID_CREDENTIALS")

    token = create_user_token(str(user.id))

    session = Session(
        user=user,
        token=token,
        status=SessionStatus.ACTIVE
    )

    hub.session_repository.insert(session)

    await hub.unit_of_work.commit(session)

    return session
