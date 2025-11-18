"""Recursos para autenticação JWT FastAPI."""

from contextvars import ContextVar
from typing import Annotated, Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError, JWTError, jwt

from backend.core.config import settings
from backend.cross_cutting.middleware.auth.models import JwtPayload
from backend.exceptions.http_exceptions import (
    InternalServerException,
    UnauthorizedException,
)
from backend.models.user import User
from backend.modules.session.session_enums import SessionStatus
from backend.modules.session.session_repository import SessionRepository
from backend.utils import date

security = HTTPBearer(auto_error=False)

requesting_user: ContextVar[
    Optional[User]
] = ContextVar('requesting_user', default=None)


async def authenticate(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session_repository: SessionRepository = Depends(),
) -> User:
    """
    Verifica token JWT e retorna usuário autenticado.

    Args:
        credentials: Credenciais HTTP com token Bearer
        session_repository: Repositório de sessões para validação

    Returns:
        User: Usuário autenticado

    Raises:
        UnauthorizedException: Token inválido, expirado ou usuário não encontrado
    """
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedException("MISSING_OR_INVALID_AUTHORIZATION_HEADER")

    token = credentials.credentials

    try:
        payload = JwtPayload(**jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        ))

    except ExpiredSignatureError as exception:
        raise UnauthorizedException("TOKEN_EXPIRED") from exception

    except JWTError as exception:
        raise UnauthorizedException("INVALID_TOKEN") from exception

    except Exception as exception:
        raise UnauthorizedException("INVALID_TOKEN") from exception

    session = await session_repository.get_by_token(token)

    if not session or session.status != SessionStatus.ACTIVE:
        raise UnauthorizedException("SESSION_NOT_FOUND_OR_INACTIVE")

    if payload.exp and date.is_past(payload.expiration_date):
        raise UnauthorizedException("TOKEN_EXPIRED")

    requesting_user.set(session.user)

    return session.user


def get_requesting_user() -> User:
    """
    Retorna o usuário atualmente autenticado.

    Args:
        current_user: Usuário autenticado via dependência

    Returns:
        User: Usuário autenticado

    Raises:
        InternalServerException: Se usuário não estiver autenticado
    """
    if requesting_user.get() is None:
        raise InternalServerException("USER_NOT_AUTHENTICATED")

    return requesting_user.get()
