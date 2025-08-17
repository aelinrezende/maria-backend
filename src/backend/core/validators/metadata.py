from typing import Any, Dict

from pydantic_core import PydanticCustomError


def validate_metadata_dict(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Valida dicionário de metadados.

    Regras:
    - Máximo 30 chaves
    - Chaves entre 1 e 50 caracteres
    """
    if len(metadata) > 30:
        raise PydanticCustomError(
            "metadata_limit",
            "metadata exceeds limit of {max_keys} keys",
            {"max_keys": 30},
        )

    for key in metadata.keys():
        if not (1 <= len(key) <= 50):
            raise PydanticCustomError(
                "metadata_key_length",
                "metadata key must be between {min_len} and {max_len} characters",
                {"min_len": 1, "max_len": 50},
            )

    return metadata
