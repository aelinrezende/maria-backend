"""
Aplicação principal do Mar.IA
"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from wireup import AsyncContainer

from backend.core.config import settings
from backend.core.database import create_vector_type


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Lifespan events para inicialização e encerramento"""
    # Startup
    try:
        logger.info(f"Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
        create_vector_type()
    except Exception as error:
        logger.error(f"Erro na inicialização: {error}")
        raise

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

    # Configurar CORS
    application.add_middleware(
        CORSMiddleware,  # type: ignore[reportUnknownArgumentType]
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.exception_handler(Exception)
    async def global_exception_handler(request, exception):
        """Handler global de exceções"""
        logger.error(f"Erro não tratado: {exception}")
        return JSONResponse(
            status_code=500, content={"detail": "Erro interno do servidor"}
        )

    return (application, {})


# Criar instância da aplicação
(app, container) = create_app()


if __name__ == "__main__":
    """Executar aplicação diretamente"""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8090,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
