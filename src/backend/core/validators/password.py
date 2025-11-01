import re

from pydantic_core import PydanticCustomError


def validate_password_strength(password: str) -> str:
    """
    Valida força da senha para requisitos mínimos de segurança.

    Requisitos:
    - Mínimo 8 caracteres
    - Pelo menos uma letra maiúscula
    - Pelo menos uma letra minúscula
    - Pelo menos um número
    - Pelo menos um caractere especial

    Args:
        password: Senha a ser validada

    Returns:
        str: Senha válida (retorna a mesma senha para uso no Pydantic)

    Raises:
        PydanticCustomError: Se a senha não atender aos requisitos
    """
    # Regex que valida todos os requisitos em uma única verificação
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]).{8,}$'

    if not re.match(pattern, password):
        raise PydanticCustomError(
            "password_weak",
            "A senha deve ter no mínimo 8 caracteres e conter pelo menos: "
            "uma letra maiúscula, uma letra minúscula, um número e um caractere especial",
        )

    return password
