from enum import Enum


class SessionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    LOGOUT = "LOGOUT"
