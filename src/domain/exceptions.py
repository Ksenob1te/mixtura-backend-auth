from fastapi import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT, HTTP_400_BAD_REQUEST, \
    HTTP_500_INTERNAL_SERVER_ERROR


class NotAuthorizedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=HTTP_401_UNAUTHORIZED,
            detail={
                "status": "error",
                "message": "Not authorized"
            }
        )


class InvalidCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=HTTP_401_UNAUTHORIZED,
            detail={
                "status": "error",
                "message": "Invalid credentials"
            }
        )


class AlreadyAuthorizedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=HTTP_409_CONFLICT,
            detail={
                "status": "error",
                "message": "Already authorized"
            }
        )


class ExceedRetryLimitException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=HTTP_409_CONFLICT,
            detail={
                "status": "error",
                "message": "Exceed retry limit"
            }
        )


class UsernameAlreadyTakenException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=HTTP_409_CONFLICT,
            detail={
                "status": "error",
                "message": "Username already taken"
            }
        )


class EmailFormatException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "message": "Email format is invalid"
            }
        )


class PasswordsDontMatchException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "message": "Passwords don't match"
            }
        )


class InternalLogicException(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": message
            }
        )
