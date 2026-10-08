class DomainError(Exception):
    """Base class for business errors; the API layer maps them to HTTP codes."""


class NotFoundError(DomainError):
    pass


class ConflictError(DomainError):
    pass


class ValidationError(DomainError):
    pass
