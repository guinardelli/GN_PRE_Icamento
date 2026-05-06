"""Custom exceptions for the application domain."""


class AppError(Exception):
    """Base error used by the app."""


class ValidationError(AppError):
    """Raised when input data is invalid."""
