"""Utilitários para geração e verificação de tokens JWT"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt

from backend.core.config import settings


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Cria um token JWT de acesso.

    Args:
        data: Dicionário com dados para incluir no token (ex: {"sub": user_id})
        expires_delta: Delta de tempo para expiração (opcional, usa padrão se não informado)

    Returns:
        str: Token JWT codificado

    Example:
        >>> token = create_access_token({"sub": "user-123"})
        >>> # Token expira em 7 dias por padrão
    """
    # Usa as configurações globais

    to_encode = data.copy()

    # Define tempo de expiração
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Padrão: 7 dias
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    # Gera token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def create_user_token(user_id: str) -> str:
    """
    Cria token JWT específico para usuário.

    Args:
        user_id: ID do usuário

    Returns:
        str: Token JWT com subject configurado

    Example:
        >>> token = create_user_token("user-123")
    """
    return create_access_token(data={"sub": user_id})
