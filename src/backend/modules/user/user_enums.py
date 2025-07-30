from enum import Enum


class UserStatus(str, Enum):
    """Status do usuário"""
    ACTIVE = "ACTIVE"
    INVITED = "INVITED"
    BLOCKED = "BLOCKED"
