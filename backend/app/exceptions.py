"""Error handling middleware and exception classes."""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import traceback
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, status_code: int = 500, error_code: str = "INTERNAL_ERROR"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class ValidationException(AppException):
    """Invalid input data."""

    def __init__(self, message: str, field: Optional[str] = None):
        self.field = field
        super().__init__(message, status_code=422, error_code="VALIDATION_ERROR")


class NotFoundException(AppException):
    """Resource not found."""

    def __init__(self, resource: str, resource_id: str):
        message = f"{resource} '{resource_id}' not found"
        super().__init__(message, status_code=404, error_code="NOT_FOUND")


class ConflictException(AppException):
    """Resource conflict (e.g., duplicate)."""

    def __init__(self, message: str):
        super().__init__(message, status_code=409, error_code="CONFLICT")


class UnauthorizedException(AppException):
    """Authentication required."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, status_code=401, error_code="UNAUTHORIZED")


class ForbiddenException(AppException):
    """Insufficient permissions."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status_code=403, error_code="FORBIDDEN")


class RateLimitException(AppException):
    """Rate limit exceeded."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429, error_code="RATE_LIMIT")


class ExternalServiceException(AppException):
    """External service failed."""

    def __init__(self, service: str, message: str):
        msg = f"{service} service error: {message}"
        super().__init__(msg, status_code=503, error_code="EXTERNAL_SERVICE_ERROR")


async def exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle AppException and return structured error response."""
    logger.error(
        f"Application error: {exc.error_code}",
        extra={
            "status_code": exc.status_code,
            "error_code": exc.error_code,
            "path": request.url.path,
            "method": request.method,
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path,
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""
    logger.warning(
        "Validation error",
        extra={
            "path": request.url.path,
            "errors": exc.errors(),
        }
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request data",
                "details": exc.errors(),
                "timestamp": datetime.utcnow().isoformat(),
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error(
        "Unhandled exception",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
            "type": type(exc).__name__,
        }
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "timestamp": datetime.utcnow().isoformat(),
            }
        }
    )


class ErrorLoggingMiddleware:
    """Middleware for detailed request/response logging."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, request: Request, call_next):
        # Log request
        logger.debug(
            f"{request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else None,
            }
        )

        try:
            response = await call_next(request)

            # Log successful response
            if response.status_code >= 400:
                logger.warning(
                    f"Response {response.status_code}",
                    extra={
                        "status_code": response.status_code,
                        "path": request.url.path,
                    }
                )

            return response

        except Exception as exc:
            logger.error(
                f"Request processing failed: {str(exc)}",
                exc_info=True,
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "type": type(exc).__name__,
                }
            )
            raise
