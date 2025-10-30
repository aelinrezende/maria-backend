"""Utilitários para geração e verificação de tokens JWT"""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

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
        expire = datetime.utcnow() + expires_delta
    else:
        # Padrão: 7 dias
        expire = datetime.utcnow() + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )

    to_encode.update({"exp": expire})

    # Gera token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.jwt_algorithm
    )

    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verifica e decodifica um token JWT.

    Args:
        token: Token JWT a ser verificado

    Returns:
        dict: Payload decodificado do token

    Raises:
        JWTError: Se token for inválido ou expirado

    Example:
        >>> payload = verify_token("eyJhbGciOiJIUzI1NiIs...")
        >>> payload["sub"]  # ID do usuário
    """
    # Usa as configurações globais

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError as e:
        raise JWTError(f"Token inválido: {str(e)}")


def extract_user_id_from_token(token: str) -> Optional[str]:
    """
    Extrai o ID do usuário (subject) do token JWT.

    Args:
        token: Token JWT

    Returns:
        Optional[str]: ID do usuário se token válido, None caso contrário

    Example:
        >>> user_id = extract_user_id_from_token(token)
        >>> if user_id:
        ...     print(f"Usuário {user_id} autenticado")
    """
    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        return user_id
    except JWTError:
        return None


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


def is_token_expired(token: str) -> bool:
    """
    Verifica se token está expirado sem lançar exceção.

    Args:
        token: Token JWT

    Returns:
        bool: True se expirado, False se válido

    Example:
        >>> if is_token_expired(token):
        ...     return "Token expirado"
    """
    try:
        verify_token(token)
        return False
    except JWTError:
        return True