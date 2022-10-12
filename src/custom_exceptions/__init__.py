from typing import Any, Tuple

from fastapi.exceptions import HTTPException


class AccessDenied(HTTPException):
    message = "Access denied"

    def __init__(self) -> None:
        super().__init__(status_code=401, detail=self.message)


class MissingEnvVar(BaseException):
    def __init__(self, args: Tuple[Any, ...]) -> None:
        self.message = f"Missing {args[0]} environmental variable"
        super().__init__(self.message)


class ExternalAuthError(HTTPException):
    message = "There was an error during your Google authentication"

    def __init__(self) -> None:
        super().__init__(status_code=401, detail=self.message)


class SystemAlreadyExists(HTTPException):
    message = "System name is already in use"

    def __init__(self) -> None:
        super().__init__(status_code=400, detail=self.message)


class SystemUserAlreadyExists(HTTPException):
    message = "User already belongs to the system"

    def __init__(self) -> None:
        super().__init__(status_code=400, detail=self.message)
