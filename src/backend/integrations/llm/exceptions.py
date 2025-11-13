"""
Exceções específicas para integração LLM.

Define hierarquia de exceções para tratamento de erros
dos diferentes provedores LLM.
"""


class LLMError(Exception):
    """Exceção base para erros de LLM."""

    def __init__(self, message: str = "Erro no provedor LLM"):
        super().__init__(message)


class LLMAuthenticationError(LLMError):
    """Erro de autenticação com provedor LLM."""

    def __init__(self, message: str = "Falha na autenticação"):
        super().__init__(message)


class LLMRateLimitError(LLMError):
    """Erro de limite de taxa atingido."""

    def __init__(self, message: str = "Limite de taxa atingido"):
        super().__init__(message)


class LLMConnectionError(LLMError):
    """Erro de conexão com provedor LLM."""

    def __init__(self, message: str = "Falha na conexão"):
        super().__init__(message)


class LLMValidationError(LLMError):
    """Erro de validação de entrada."""

    def __init__(self, message: str = "Dados de entrada inválidos"):
        super().__init__(message)


class ClaudeError(LLMError):
    """Erro específico do Claude."""

    def __init__(self, message: str = "Erro na API do Claude"):
        super().__init__(message)


class GeminiError(LLMError):
    """Erro específico do Gemini."""

    def __init__(self, message: str = "Erro na API do Gemini"):
        super().__init__(message)


class GLMError(LLMError):
    """Erro específico do GLM."""

    def __init__(self, message: str = "Erro na API do GLM"):
        super().__init__(message)
