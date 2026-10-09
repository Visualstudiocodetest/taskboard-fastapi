class DomainError(Exception):
    """Base class for business errors; the API layer maps them to HTTP codes."""


class NotFoundError(DomainError):
    """Entity does not exist (HTTP 404)."""


class ConflictError(DomainError):
    """Violates a uniqueness rule (HTTP 409)."""


class ValidationError(DomainError):
    """Business-rule violation the schema cannot catch (HTTP 422)."""
