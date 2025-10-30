"""Utilitários para hashing e verificação de senhas"""

from secrets import token_urlsafe

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


def generate_password_reset_token(length: int = 32) -> str:
    """
    Gera token seguro para reset de senha.

    Args:
        length: Comprimento do token (padrão: 32 caracteres)

    Returns:
        str: Token URL-safe seguro para reset de senha

    Example:
        >>> generate_password_reset_token()
        'AbCdEf123456...'
    """
    return token_urlsafe(length)


def generate_secure_random_password(length: int = 12) -> str:
    """
    Gera senha aleatória segura (para casos específicos).

    Args:
        length: Comprimento da senha gerada (padrão: 12)

    Returns:
        str: Senha aleatória com todos os requisitos de segurança

    Note:
        Esta função deve ser usada apenas em casos específicos
        como reset de senha por administrador.
    """
    import random
    import string

    # Garantir que tenha pelo menos um de cada tipo
    password = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice('!@#$%^&*()_+-=[]{}|;:,.<>?')
    ]

    # Preencher o resto com caracteres aleatórios
    all_chars = string.ascii_letters + string.digits + '!@#$%^&*()_+-=[]{}|;:,.<>?'
    password.extend(random.choices(all_chars, k=length - 4))

    # Embaralhar para não ter padrão fixo
    random.shuffle(password)

    return ''.join(password)
