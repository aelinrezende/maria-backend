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
