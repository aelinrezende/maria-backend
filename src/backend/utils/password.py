"""Utilitários para hashing e verificação de senhas"""


from passlib.context import CryptContext

# Contexto do bcrypt com configurações seguras
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Número de rounds para maior segurança
)


def hash_password(password: str) -> str:
    """
    Gera hash seguro da senha usando bcrypt.

    Args:
        password: Senha em texto plano

    Returns:
        str: Hash da senha gerado com bcrypt

    Example:
        >>> hash_password("Senha123@")
        '$2b$12$...'
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se senha em texto plano corresponde ao hash armazenado.

    Args:
        plain_password: Senha em texto plano para verificar
        hashed_password: Hash da senha armazenado no banco

    Returns:
        bool: True se senhas coincidem, False caso contrário

    Example:
        >>> verify_password("Senha123@", stored_hash)
        True
    """
    return pwd_context.verify(plain_password, hashed_password)
