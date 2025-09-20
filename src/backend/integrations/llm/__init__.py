"""
Integração LLM - Interface genérica para Large Language Models.

Este módulo fornece uma interface unificada para comunicação
com diferentes provedores de LLM (Claude, Gemini, etc.).

Componentes principais:
- Protocol: Interface comum para todos os providers
- Models: Estruturas de dados compartilhadas
- Exceptions: Hierarquia de exceções específicas
- Providers: Implementações para Claude e Gemini
- Factory: Criação simplificada de providers

Exemplo de uso:
    ```python
    from backend.integrations.llm import LLMFactory, Message
    
    # Criar provider
    provider = LLMFactory.create_claude_provider(api_key="sk-...")
    
    # Usar provider
    messages = [Message(role="user", content="Olá!")]
    async for chunk in provider.stream_chat(messages):
        print(chunk.content, end="")
    ```
"""

from backend.interfaces import ILLMConfig

from .exceptions import (
    ClaudeError,
    GeminiError,
    LLMAuthenticationError,
    LLMConnectionError,
    LLMError,
    LLMRateLimitError,
    LLMValidationError,
)
from .models import Message, StreamChunk
from .protocol import ILLMProvider

__all__ = [
    # Protocol
    "ILLMProvider",

    # Models
    "Message",
    "StreamChunk",
    "ILLMConfig",

    # Exceptions
    "LLMError",
    "LLMAuthenticationError",
    "LLMRateLimitError",
    "LLMConnectionError",
    "LLMValidationError",
    "ClaudeError",
    "GeminiError",
]
