from uuid import UUID
from typing import Optional

from fastapi import status
from fastapi.exceptions import HTTPException


class ObjectNotFoundException(HTTPException):
    def __init__(self, id: UUID) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Object with {id=} does not exist",
        )


class GenericBadRequestException(HTTPException):
    def __init__(self, detail: Optional[str] = None, headers: Optional[dict[str, str]] = None) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            headers=headers
        )


class BadRequestFromRaisedException(GenericBadRequestException):
    def __init__(self, exception: Exception, headers: Optional[dict[str, str]] = None) -> None:
        super().__init__(detail=str(exception), headers=headers)


ConflictErrorException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Conflict Error"
)
