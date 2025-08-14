"""Registro central de tratamento de exceções FastAPI.

Centraliza a tradução de qualquer Exception em uma resposta JSON.
"""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger

from .http_exceptions import (
    ConflictException,
    HttpException,
    InternalServerException,
)


def register_exception_handler(app: FastAPI) -> None:
    """Registra handler global de exceções."""

    @app.exception_handler(Exception)
    async def _exception_handler(_request: Request, exc: Exception):
        if isinstance(exc, HttpException):
            error = exc
        elif _is_unique_violation(exc):
            error = ConflictException()
        else:
            error = InternalServerException()
            logger.error(f"Erro não tratado: {exc}", exc_info=exc)

        return JSONResponse(status_code=error.status_code, content=error.to_dict())


def _is_unique_violation(exc: Exception) -> bool:
    msg = str(exc).lower()
    return ("unique" in msg and "constraint" in msg) or "duplicate key" in msg
