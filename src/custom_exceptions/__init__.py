from typing import Any, Tuple

from fastapi.exceptions import HTTPException


class CustomHTTPException(HTTPException):
    message: str

    def __init__(self, status_code: int, message: str) -> None:
        self.message = message
        super().__init__(status_code=status_code, detail=self.message)


class CustomExternalException(CustomHTTPException):
    extra: Tuple[Any, ...]

    def __init__(self, message: str, args: Tuple[Any, ...]) -> None:
        self.extra = args
        super().__init__(status_code=503, message=message)


class AccessDenied(CustomHTTPException):
    def __init__(self) -> None:
        message = "Access denied"
        super().__init__(status_code=403, message=message)


class AuthenticationFailed(CustomHTTPException):
    def __init__(self) -> None:
        message = "Authentication failed"
        super().__init__(status_code=401, message=message)


class CVEDoesNotExist(CustomHTTPException):
    def __init__(self) -> None:
        message = "The CVE you provided does not exist in the NIST database"
        super().__init__(status_code=400, message=message)


class DynamoDBException(CustomExternalException):
    def __init__(self, args: Tuple[Any, ...]) -> None:
        message = "There was an error in the request to the database"
        super().__init__(message=message, args=args)


class MaxItemsLimit(CustomHTTPException):
    def __init__(self) -> None:
        message = "Bulk operations have a limit of 20 items"
        super().__init__(status_code=400, message=message)


class MissingEnvVar(BaseException):
    def __init__(self, args: Tuple[Any, ...]) -> None:
        self.message = f"Missing {args[0]} environmental variable"
        super().__init__(self.message)


class ExternalAuthError(CustomExternalException):
    def __init__(self, args: Tuple[Any, ...]) -> None:
        message = "There was an error during your Google authentication"
        super().__init__(message=message, args=args)


class NISTAPIError(CustomExternalException):
    def __init__(self, args: Tuple[Any, ...]) -> None:
        message = "There was an error querying the NIST API. Try again later"
        super().__init__(message=message, args=args)


class NISTResponseError(CustomHTTPException):
    def __init__(self) -> None:
        message = "The request from the NIST API dit not finish successfully"
        super().__init__(status_code=503, message=message)


class SystemAlreadyExists(CustomHTTPException):
    def __init__(self) -> None:
        message = "System name is already in use"
        super().__init__(status_code=400, message=message)


class SystemUserAlreadyExists(CustomHTTPException):
    def __init__(self) -> None:
        message = "User already belongs to the system"
        super().__init__(status_code=400, message=message)


class SystemVulnerabilityAlreadyExists(CustomHTTPException):
    def __init__(self) -> None:
        message = "Vulnerability is already reported to the system"
        super().__init__(status_code=400, message=message)


class SystemVulnerabilityDoesNotExist(CustomHTTPException):
    def __init__(self) -> None:
        message = "Vulnerability does not exist in the system"
        super().__init__(status_code=400, message=message)
