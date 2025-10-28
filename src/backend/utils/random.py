"""Utilitários relacionados a operações aleatórias."""


import secrets


def generate_code(length: int = 10) -> str:
    """
    Gera um código de convite criptograficamente seguro.

    Args:
        length: Comprimento do código (padrão: 10)

    Returns:
        str: Código de convite único e seguro
    """
    return secrets.token_hex(length)[:length].upper()
