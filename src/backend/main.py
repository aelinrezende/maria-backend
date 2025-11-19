"""
Aplicação principal do Mar.IA
"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from wireup import AsyncContainer, create_async_container
from wireup.integration.fastapi import setup

from backend.core import DatabaseConnection, UnitOfWork, settings
from backend.core.migrations import MigrationRunner
from backend.exceptions.handler import register_exception_handler
from backend.integrations.embeddings import LocalSentenceTransformerProvider
from backend.integrations.mailgun import MailGun
from backend.modules.auth.auth_router import AuthRouter, auth_router
from backend.modules.chunk.chunk_repository import ChunkRepository
from backend.modules.chunk.chunk_service import ChunkService
from backend.modules.document.document_repository import DocumentRepository
from backend.modules.document.document_router import DocumentRouter, document_router
from backend.modules.document.document_service import DocumentService
from backend.modules.me.me_router import MeRouter, me_router
from backend.modules.message.message_repository import MessageRepository
from backend.modules.rag.rag_router import RAGRouter, rag_router
from backend.modules.rag.rag_service import RAGService
from backend.modules.session.session_repository import SessionRepository
from backend.modules.session.session_service import SessionService
from backend.modules.user.user_repository import UserRepository
from backend.modules.user.user_router import user_router
from backend.modules.user.user_service import UserService


@asynccontextmanager
async def lifespan(_: FastAPI, connection=DatabaseConnection()):
    """Lifespan events para inicialização e encerramento"""
    # Startup
    try:
        logger.info(f"Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")

        if settings.AUTO_MIGRATIONS:
            await MigrationRunner(connection).apply_migrations()

        await connection.create_vector_type()
    except Exception as error:
        logger.error(f"Erro na inicialização: {error}")
        raise
    finally:
        await connection.session.close()

    yield

    # Shutdown
    logger.info("Encerrando aplicação")


def create_app() -> tuple[FastAPI, AsyncContainer]:
    """Cria a aplicação FastAPI"""

    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Sistema RAG Agentic para população trans",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Incluir routers
    application.include_router(user_router)
    application.include_router(auth_router)
    application.include_router(me_router)
    application.include_router(document_router)
    application.include_router(rag_router)

    # Configurar CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Injeção de dependências
    dependencies = create_async_container(
        services=[
            # Database
            DatabaseConnection,

            # Integrations
            MailGun,
            LocalSentenceTransformerProvider,

            # Auth
            AuthRouter,

            # Session
            SessionRepository,
            SessionService,

            # Profile
            MeRouter,

            # Message
            MessageRepository,

            # User
            UserRepository,
            UserService,

            # Document
            DocumentRouter,
            DocumentService,
            DocumentRepository,

            # Chunk
            ChunkService,
            ChunkRepository,

            # RAG
            RAGRouter,
            RAGService,

            # Outros
            UnitOfWork

        ],
        parameters={
            "debug": settings.DEBUG
        },
    )

    # Registrar handler global único
    register_exception_handler(application)

    return (application, dependencies)


# Cria instância da aplicação
(app, container) = create_app()

# Configura injeção de dependências
setup(container, app)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8090,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
