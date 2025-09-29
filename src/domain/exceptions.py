from fastapi import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT


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
