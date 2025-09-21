"""
Factory para criação de providers LLM.

Centraliza a lógica de criação e configuração dos diferentes
providers de LLM disponíveis no sistema.
"""


from typing import TYPE_CHECKING, Literal, Optional

from backend.core.config import settings
from backend.integrations.llm.models import ClaudeConfig

from . import ILLMConfig
from .claude import ClaudeProvider
from .exceptions import LLMValidationError

if TYPE_CHECKING:
    from backend.integrations.llm import ILLMProvider


class LLMFactory:
    """
    Factory para criação de providers LLM.

    Responsável por instanciar o provider correto baseado
    na configuração fornecida.
    """

    @staticmethod
    def create_provider(
            model: Literal["claude", "gemini"] = settings.DEFAULT_LLM_PROVIDER,
            config: Optional[ILLMConfig] = None
    ) -> "ILLMProvider":
        """
        Cria um provider LLM baseado na configuração.

        Args:
            model: Tipo do modelo/provedor (ex: "claude", "gemini")
            config: Configuração do provider (ILLMConfig)

        Returns:
            LLMProvider: Instância do provider configurado

        Raises:
            LLMValidationError: Se a configuração não for válida
        """
        match model:
            case "claude":
                return ClaudeProvider(config or ClaudeConfig())
            case "gemini":
                # TODO: Implementar GeminiProvider
                pass
            case _:
                raise LLMValidationError(
                    f"Tipo de modelo não suportado: {model}"
                )
