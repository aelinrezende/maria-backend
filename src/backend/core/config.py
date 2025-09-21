"""
Configurações centralizadas do sistema Mar.IA
"""

import os

from loguru import logger
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações do sistema Mar.IA"""

    # Configurações básicas
    APP_NAME: str = "Mar.IA"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Configurações de banco de dados
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/maria_db"

    # Configurações de embeddings
    # Modelo multilingue forte para retrieval
    EMBEDDING_MODEL: str = "intfloat/multilingual-e5-base"
    EMBEDDING_DIMENSION: int = 768
    EMBEDDING_PROVIDER: str = "local"

    # Configurações de segurança
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Configurações de logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/maria.log"

    # Configurações de CORS
    ALLOWED_ORIGINS: list[str] = ["*"]

    # Configurações de Mailgun
    MAILGUN_API_KEY: str = "your-mailgun-api-key"
    MAILGUN_DOMAIN: str = "your-mailgun-domain"
    MAILGUN_API_URL: str = "https://api.mailgun.net"
    MAILGUN_TEST_EMAIL: str = "aelinrezende@gmail.com"

    # Configurações de Chunking
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50

    # Configurações LLM - Interface Genérica

    # Claude (Anthropic)
    CLAUDE_API_KEY: str = "your-claude-api-key-here"
    CLAUDE_MODEL: str = "claude-3-7-sonnet-20250219"
    CLAUDE_MAX_TOKENS: int = 4096
    CLAUDE_TEMPERATURE: float = 0.7

    # Gemini (Google)
    GEMINI_API_KEY: str = "your-gemini-api-key-here"
    GEMINI_MODEL: str = "gemini-2.5-pro"
    GEMINI_MAX_TOKENS: int = 4096
    GEMINI_TEMPERATURE: float = 0.7

    # Configurações gerais LLM
    DEFAULT_LLM_PROVIDER: str = "gemini"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Instância global das configurações
settings = Settings()


def setup_logging():
    """Configura o sistema de logging"""
    logger.remove()  # Remove handlers padrão

    # Handler para console
    logger.add(
        lambda msg: print(msg, end=""),
        level=settings.LOG_LEVEL,
        format="""
            <green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:
            <cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>""",
    )

    # Handler para arquivo
    os.makedirs("logs", exist_ok=True)
    logger.add(
        settings.LOG_FILE,
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="1 day",
        retention="30 days",
    )


def get_settings() -> Settings:
    """Retorna as configurações do sistema"""
    return settings
