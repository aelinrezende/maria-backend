"""
Modelos de dados para integração LLM.

Define estruturas de dados tipadas para mensagens, chunks de streaming
e configurações dos provedores LLM.
"""

from dataclasses import dataclass
from typing import Literal


@dataclass
class Message:
    """Representa uma mensagem no chat."""
    role: Literal["user", "assistant", "system"]
    content: str


@dataclass
class StreamChunk:
    """Representa um chunk de resposta streaming."""
    content: str
    is_final: bool = False
