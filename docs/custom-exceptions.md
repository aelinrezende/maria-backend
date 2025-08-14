# Custom Exceptions Documentation

## Overview

This document describes the custom exception system implemented for the Mar.IA backend application. The system provides structured error handling with appropriate HTTP status codes for different error scenarios.

## Exception Hierarchy

```
BaseApplicationException
├── EntityNotFoundException (404)
├── ValidationException (400)
├── AuthenticationException (401)
├── AuthorizationException (403)
├── ConflictException (409)
└── BusinessLogicException (422)
```

## Exception Classes

### `BaseApplicationException`

Base class for all application-specific exceptions.

**Attributes:**
- `message`: Human-readable error message
- `error_code`: Machine-readable error code
- `details`: Additional error details (dict)

### `EntityNotFoundException`

Raised when a database entity is not found.

**HTTP Status Code:** 404 Not Found

**Usage:**
```python
# With identifier
raise EntityNotFoundException("User", "123")
# Output: "User with identifier '123' not found"

# Without identifier
raise EntityNotFoundException("Document")
# Output: "Document not found with the given criteria"
```

**Attributes:**
- `entity_name`: Name of the entity type
- `identifier`: Optional identifier value

### `ValidationException`

Raised when data validation fails.

**HTTP Status Code:** 400 Bad Request

**Usage:**
```python
field_errors = {"email": "Invalid format", "age": "Must be positive"}
raise ValidationException("Validation failed", field_errors)
```

**Attributes:**
- `field_errors`: Dictionary of field-specific error messages

### `AuthenticationException`

Raised when authentication fails.

**HTTP Status Code:** 401 Unauthorized

**Usage:**
```python
raise AuthenticationException("Invalid credentials")
```

### `AuthorizationException`

Raised when authorization fails.

**HTTP Status Code:** 403 Forbidden

**Usage:**
```python
raise AuthorizationException("Insufficient permissions")
```

### `ConflictException`

Raised when there's a conflict with existing data.

**HTTP Status Code:** 409 Conflict

**Usage:**
```python
raise ConflictException("Email already exists")
```

### `BusinessLogicException`

Raised when business logic validation fails.

**HTTP Status Code:** 422 Unprocessable Entity

**Usage:**
```python
raise BusinessLogicException("Cannot delete user with active sessions")
```

## Integration with BaseRepository

The `BaseRepository` class has been updated to use custom exceptions:

### Before
```python
async def find_by_id_or_fail(self, id: str) -> T:
    entity = await self.__session.get(T, id)
    if entity is None:
        # TODO: Criar uma exceção personalizada para não encontrado
        raise ValueError(f"Entity with id {id} not found")
    return entity
```

### After
```python
async def find_by_id_or_fail(self, id: str) -> T:
    entity = await self.__session.get(T, id)
    if entity is None:
        raise EntityNotFoundException(
            entity_name=self.model.__name__,
            identifier=id
        )
    return entity
```

## HTTP Response Format

When custom exceptions are raised, they are automatically converted to appropriate HTTP responses:

### EntityNotFoundException Response
```json
{
  "detail": "User with identifier '123' not found",
  "error_code": "ENTITY_NOT_FOUND",
  "entity_name": "User",
  "identifier": "123"
}
```

### ValidationException Response
```json
{
  "detail": "Validation failed",
  "error_code": "VALIDATION_ERROR",
  "field_errors": {
    "email": "Invalid format",
    "age": "Must be positive"
  }
}
```

## Usage in Services

Services can use these exceptions to provide clear error handling:

```python
class UserService:
    async def get_user(self, user_id: str) -> User:
        try:
            return await self.repository.find_by_id_or_fail(user_id)
        except EntityNotFoundException:
            # Exception will be automatically handled by FastAPI
            raise
    
    async def create_user(self, user_data: dict) -> User:
        # Validate email uniqueness
        existing = await self.repository.find_one(User.email == user_data["email"])
        if existing:
            raise ConflictException("Email already exists")
        
        # Validate required fields
        if not user_data.get("email"):
            raise ValidationException(
                "Validation failed",
                {"email": "Email is required"}
            )
        
        return await self.repository.insert(User(**user_data))
```

## Exception Handler Registration

Exception handlers are automatically registered in the FastAPI application:

```python
# In main.py
application.add_exception_handler(EntityNotFoundException, entity_not_found_handler)
application.add_exception_handler(ValidationException, validation_exception_handler)
application.add_exception_handler(AuthenticationException, authentication_exception_handler)
application.add_exception_handler(AuthorizationException, authorization_exception_handler)
application.add_exception_handler(ConflictException, conflict_exception_handler)
application.add_exception_handler(BusinessLogicException, business_logic_exception_handler)
application.add_exception_handler(BaseApplicationException, base_application_exception_handler)
```

## Best Practices

1. **Use specific exceptions**: Choose the most appropriate exception type for the error scenario
2. **Provide meaningful messages**: Include context that helps users understand the issue
3. **Include relevant details**: Use the `details` parameter for additional context
4. **Don't catch and re-raise**: Let FastAPI handle the exceptions automatically
5. **Log appropriately**: Exception handlers automatically log warnings/errors with appropriate levels

## Future Extensions

The exception system can be easily extended by:

1. Adding new exception classes that inherit from `BaseApplicationException`
2. Creating corresponding exception handlers
3. Registering the handlers in the FastAPI application

Example:
```python
class ExternalServiceException(BaseApplicationException):
    def __init__(self, service_name: str, message: str = "External service error"):
        super().__init__(
            message=f"{service_name}: {message}",
            error_code="EXTERNAL_SERVICE_ERROR"
        )
        self.service_name = service_name
```