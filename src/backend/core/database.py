"""
Configuração do banco de dados
"""


from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import text
from wireup import service

from .config import settings


@service(lifetime="scoped")
class DatabaseConnection:
    """Classe para gerenciar a conexão com o banco de dados"""

    def __init__(self) -> None:
        """Inicializa a conexão com o banco de dados usando as configurações definidas"""
        self.engine = create_async_engine(
            settings.DATABASE_URL, echo=settings.DEBUG, pool_pre_ping=True, pool_recycle=300
        )
        self._session = AsyncSession(self.engine, expire_on_commit=False)

    async def create_vector_type(self) -> None:
        """Cria o tipo de dado vetorial no banco de dados"""
        async with self.engine.begin() as connection:
            await connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

    @property
    def session(self) -> AsyncSession:
        """Retorna uma sessão assíncrona para interação com o banco de dados"""
        return self._session
