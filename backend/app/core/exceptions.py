from fastapi import HTTPException


class NotFoundError(HTTPException):
    """404 Not Found error."""
    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(status_code=404, detail=detail)


class UnauthorizedError(HTTPException):
    """401 Unauthorized error."""
    def __init__(self, detail: str = "Not authenticated") -> None:
        super().__init__(status_code=401, detail=detail)


class ForbiddenError(HTTPException):
    """403 Forbidden error."""
    def __init__(self, detail: str = "Not authorized") -> None:
        super().__init__(status_code=403, detail=detail)


class BadRequestError(HTTPException):
    """400 Bad Request error."""
    def __init__(self, detail: str = "Bad request") -> None:
        super().__init__(status_code=400, detail=detail)


class ServiceUnavailableError(HTTPException):
    """503 Service Unavailable error."""
    def __init__(self, detail: str = "Upstream service unavailable") -> None:
        super().__init__(status_code=503, detail=detail)
