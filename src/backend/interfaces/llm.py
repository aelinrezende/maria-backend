
from typing import Protocol


class ILLMConfig(Protocol):
    """Base para configurações de LLM."""
    api_key: str
    model: str
    temperature: float
    max_tokens: int
