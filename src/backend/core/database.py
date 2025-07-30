"""
Configuração do banco de dados
"""

from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from .config import settings

# Engine assíncrono do banco de dados
database_engine = create_async_engine(
    settings.DATABASE_URL, echo=settings.DEBUG, pool_pre_ping=True, pool_recycle=300
)


async def create_vector_type():
    """Cria o tipo de dado vetorial para o banco de dados"""
    async with database_engine.begin() as connection:
        await connection.run_sync(
            lambda engine: engine.execute(
                "CREATE EXTENSION IF NOT EXISTS vector;"
            )
        )


@asynccontextmanager
async def get_database_session():
    """Retorna uma sessão assíncrona do banco de dados"""
    database_session = AsyncSession(database_engine)

    try:
        yield database_session
    finally:
        await database_session.close()
