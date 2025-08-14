"""
Exception handlers for FastAPI application.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger

from .exceptions import (
    BaseApplicationException,
    EntityNotFoundException,
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    ConflictException,
    BusinessLogicException,
)


async def entity_not_found_handler(request: Request, exc: EntityNotFoundException) -> JSONResponse:
    """Handle EntityNotFoundException and return 404 response."""
    logger.warning(f"Entity not found: {exc.message}")
    
    return JSONResponse(
        status_code=404,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
            "entity_name": exc.entity_name,
            "identifier": exc.identifier,
            **exc.details
        }
    )


async def validation_exception_handler(request: Request, exc: ValidationException) -> JSONResponse:
    """Handle ValidationException and return 400 response."""
    logger.warning(f"Validation error: {exc.message}")
    
    return JSONResponse(
        status_code=400,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
            "field_errors": exc.field_errors,
            **exc.details
        }
    )


async def authentication_exception_handler(request: Request, exc: AuthenticationException) -> JSONResponse:
    """Handle AuthenticationException and return 401 response."""
    logger.warning(f"Authentication error: {exc.message}")
    
    return JSONResponse(
        status_code=401,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
            **exc.details
        }
    )


async def authorization_exception_handler(request: Request, exc: AuthorizationException) -> JSONResponse:
    """Handle AuthorizationException and return 403 response."""
    logger.warning(f"Authorization error: {exc.message}")
    
    return JSONResponse(
        status_code=403,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
            **exc.details
        }
    )


async def conflict_exception_handler(request: Request, exc: ConflictException) -> JSONResponse:
    """Handle ConflictException and return 409 response."""
    logger.warning(f"Conflict error: {exc.message}")
    
    return JSONResponse(
        status_code=409,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
            **exc.details
        }
    )


async def business_logic_exception_handler(request: Request, exc: BusinessLogicException) -> JSONResponse:
    """Handle BusinessLogicException and return 422 response."""
    logger.warning(f"Business logic error: {exc.message}")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
            **exc.details
        }
    )


async def base_application_exception_handler(request: Request, exc: BaseApplicationException) -> JSONResponse:
    """Handle any other BaseApplicationException and return 500 response."""
    logger.error(f"Application error: {exc.message}")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
            **exc.details
        }
    )