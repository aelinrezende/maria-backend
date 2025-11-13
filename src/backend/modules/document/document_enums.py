from enum import Enum


class DocumentKind(str, Enum):
    """Enumeração para tipos de documentos na base de conhecimento"""

    HORMONAL_SAFETY = "HORMONAL_SAFETY"
    LEGAL_PROCEDURES = "LEGAL_PROCEDURES"
    HEALTH_INSURANCE = "HEALTH_INSURANCE"


class DocumentStatus(str, Enum):
    """Enumeração para status dos documentos na base de conhecimento"""

    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    BLOCKED = "BLOCKED"
