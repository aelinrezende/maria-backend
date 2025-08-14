"""
Custom exceptions for the backend application.
"""

from typing import Any, Dict, Optional


class BaseApplicationException(Exception):
    """Base exception class for all application-specific exceptions."""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class EntityNotFoundException(BaseApplicationException):
    """Exception raised when an entity is not found in the database."""
    
    def __init__(
        self, 
        entity_name: str = "Entity", 
        identifier: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if identifier:
            message = f"{entity_name} with identifier '{identifier}' not found"
        else:
            message = f"{entity_name} not found with the given criteria"
        
        super().__init__(
            message=message,
            error_code="ENTITY_NOT_FOUND",
            details=details
        )
        self.entity_name = entity_name
        self.identifier = identifier


class ValidationException(BaseApplicationException):
    """Exception raised when data validation fails."""
    
    def __init__(
        self, 
        message: str = "Validation failed",
        field_errors: Optional[Dict[str, str]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details
        )
        self.field_errors = field_errors or {}


class AuthenticationException(BaseApplicationException):
    """Exception raised when authentication fails."""
    
    def __init__(
        self, 
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            details=details
        )


class AuthorizationException(BaseApplicationException):
    """Exception raised when authorization fails."""
    
    def __init__(
        self, 
        message: str = "Access denied",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            details=details
        )


class ConflictException(BaseApplicationException):
    """Exception raised when there's a conflict with existing data."""
    
    def __init__(
        self, 
        message: str = "Resource conflict",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="CONFLICT_ERROR",
            details=details
        )


class BusinessLogicException(BaseApplicationException):
    """Exception raised when business logic validation fails."""
    
    def __init__(
        self, 
        message: str = "Business logic error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="BUSINESS_LOGIC_ERROR",
            details=details
        )