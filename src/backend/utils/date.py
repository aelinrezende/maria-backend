"""Utilitários relacionados a operações com datas."""

from datetime import datetime, timedelta, timezone


def add_days(days: int) -> datetime:
    """
    Adiciona dias à data atual.

    Args:
        days: Número de dias a adicionar

    Returns:
        datetime: Data resultante
    """
    return datetime.now(timezone.utc) + timedelta(days=days)


def is_past(date_to_check: datetime) -> bool:
    """
    Verifica se uma data está no passado.

    Args:
        date_to_check: Data a ser verificada

    Returns:
        bool: True se a data estiver no passado
    """
    return _ensure_time_zone(date_to_check) < datetime.now()


def _ensure_time_zone(date: datetime) -> datetime:
    """
    Remove a informação de fuso horário de um objeto datetime.

    Args:
        date: Objeto datetime com fuso horário

    Returns:
        datetime: Objeto datetime sem fuso horário
    """
    if date.tzinfo is None:
        return date.replace(tzinfo=timezone.utc)

    return date.astimezone(timezone.utc)
