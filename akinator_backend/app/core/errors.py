"""Error definitions and standardized error models."""

from typing import Optional, Any
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standardized API error response."""
    error_code: str
    message: str
    message_bn: str
    details: Optional[Any] = None


class AppException(Exception):
    """Base application exception."""
    def __init__(
        self,
        error_code: str,
        message: str,
        message_bn: str,
        status_code: int = 400,
        details: Optional[Any] = None
    ):
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.message_bn = message_bn
        self.status_code = status_code
        self.details = details


class SessionNotFoundError(AppException):
    def __init__(self, session_id: str):
        super().__init__(
            error_code="SESSION_NOT_FOUND",
            message=f"Game session '{session_id}' was not found or has expired.",
            message_bn="খেলার সেশনটি পাওয়া যায়নি অথবা মেয়াদ শেষ হয়ে গেছে। নতুন খেলা শুরু করুন।",
            status_code=404
        )


class SessionStateConflictError(AppException):
    def __init__(self, message: str, message_bn: str):
        super().__init__(
            error_code="SESSION_STATE_CONFLICT",
            message=message,
            message_bn=message_bn,
            status_code=409
        )


class DatabaseUnavailableError(AppException):
    def __init__(self, detail: str = ""):
        super().__init__(
            error_code="DATABASE_UNAVAILABLE",
            message="Database connection error.",
            message_bn="ডাটাবেসের সাথে সংযোগ স্থাপন করা সম্ভব হয়নি।",
            status_code=503,
            details=detail
        )
