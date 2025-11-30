class DomainException(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


class NotAuthorizedException(DomainException):
    def __init__(self):
        super().__init__(status_code=401, message="Not authorized")


class InvalidCredentialsException(DomainException):
    def __init__(self):
        super().__init__(status_code=401, message="Invalid credentials")


class AlreadyAuthorizedException(DomainException):
    def __init__(self):
        super().__init__(status_code=409, message="Already authorized")


class ExceedRetryLimitException(DomainException):
    def __init__(self):
        super().__init__(status_code=409, message="Exceed retry limit")


class UsernameAlreadyTakenException(DomainException):
    def __init__(self):
        super().__init__(status_code=409, message="Username already taken")


class EmailFormatException(DomainException):
    def __init__(self):
        super().__init__(status_code=400, message="Email format is invalid")


class PasswordsDontMatchException(DomainException):
    def __init__(self):
        super().__init__(status_code=400, message="Passwords don't match")


class NotFoundProviderException(DomainException):
    def __init__(self):
        super().__init__(status_code=404, message="Provider not found")


class ProviderAlreadyLinkedException(DomainException):
    def __init__(self):
        super().__init__(status_code=400, message="Provider already linked")


class IntegrationLimitException(DomainException):
    def __init__(self):
        super().__init__(status_code=400, message="Integration limit exceeded")


class WrongOAuthCodeException(DomainException):
    def __init__(self):
        super().__init__(status_code=404, message="Given code not correct")


class NotEnabledForAuthProviderException(DomainException):
    def __init__(self):
        super().__init__(status_code=403, message="Provider only for integration")


class InternalLogicException(DomainException):
    def __init__(self, message: str):
        super().__init__(status_code=500, message=message)
