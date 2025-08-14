"""
Aplicação principal do Mar.IA
"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from wireup import AsyncContainer, create_async_container
from wireup.integration.fastapi import setup

from backend.core.config import settings
from backend.core.database import DatabaseConnection
from backend.core.exceptions import (
    BaseApplicationException,
    EntityNotFoundException,
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    ConflictException,
    BusinessLogicException,
)
from backend.core.exception_handlers import (
    entity_not_found_handler,
    validation_exception_handler,
    authentication_exception_handler,
    authorization_exception_handler,
    conflict_exception_handler,
    business_logic_exception_handler,
    base_application_exception_handler,
)
from backend.integrations.mailgun import MailGun
from backend.modules.auth.auth_router import AuthRouter, auth_router
from backend.modules.user.user_repository import UserRepository
from backend.modules.user.user_router import user_router
from backend.modules.user.user_service import UserService


@asynccontextmanager
async def lifespan(_: FastAPI, connection=DatabaseConnection()):
    """Lifespan events para inicialização e encerramento"""
    # Startup
    try:
        logger.info(f"Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
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

            # Auth
            AuthRouter,

            # User
            UserRepository,
            UserService,
        ],
        parameters={
            "debug": settings.DEBUG
        },
    )

    # Register custom exception handlers
    application.add_exception_handler(EntityNotFoundException, entity_not_found_handler)
    application.add_exception_handler(ValidationException, validation_exception_handler)
    application.add_exception_handler(AuthenticationException, authentication_exception_handler)
    application.add_exception_handler(AuthorizationException, authorization_exception_handler)
    application.add_exception_handler(ConflictException, conflict_exception_handler)
    application.add_exception_handler(BusinessLogicException, business_logic_exception_handler)
    application.add_exception_handler(BaseApplicationException, base_application_exception_handler)

    @application.exception_handler(Exception)
    async def global_exception_handler(request, exception):
        """Handler global de exceções"""
        logger.error(f"Erro não tratado: {exception}")
        return JSONResponse(
            status_code=500, content={"detail": "Erro interno do servidor"}
        )

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
