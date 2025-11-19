from enum import Enum


class MessageRole(str, Enum):
    """Enumeração para papéis de autor em mensagens"""

    USER = "USER"
    SYSTEM = "SYSTEM"
    ASSISTANT = "ASSISTANT"
