"""Validadores e tipos Annotated para DTOs.

Este pacote expõe funções puras de validação e, para uso em DTOs, tipos Annotated
já configurados com BeforeValidator para reduzir repetição nas declarações.
"""

from typing import Annotated, Any, Dict

from pydantic import BeforeValidator

from .metadata import validate_metadata_dict

MetadataDict = Annotated[
    Dict[str, Any],
    BeforeValidator(validate_metadata_dict)
]

__all__ = [
    # Funções
    "validate_metadata_dict",

    # Tipos
    "MetadataDict",
]
