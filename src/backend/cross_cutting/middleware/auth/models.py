from datetime import datetime

from sqlmodel import SQLModel


class JwtPayload(SQLModel):
    """Modelo para o payload do token JWT."""
    sub: str
    exp: float

    @property
    def expiration_date(self) -> datetime:
        """Retorna a data de expiração como objeto datetime."""
        return datetime.fromtimestamp(self.exp)
