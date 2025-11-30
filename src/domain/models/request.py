from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.domain.constants import PASSWORD_REGEX, USERNAME_REGEX


class TokenRequest(BaseModel):
    token: str


class UsernameRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=USERNAME_REGEX)


class UsernameUpdateRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=USERNAME_REGEX)
    user_id: UUID


def strip_and_lower(v: object) -> str:
    return str(v).strip().lower()


class EmailRequest(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return strip_and_lower(v)


class EmailVerifyRequest(BaseModel):
    email: EmailStr
    token: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return strip_and_lower(v)


class PasswordConfirmRequest(BaseModel):
    email: EmailStr
    token: str
    auth_token: str | None
    password: str = Field(pattern=PASSWORD_REGEX, min_length=6, max_length=32)
    repeat_password: str = Field(pattern=PASSWORD_REGEX, min_length=6, max_length=32)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return strip_and_lower(v)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class SignupConfirmRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50, pattern=USERNAME_REGEX)
    token: str
    password: str = Field(pattern=PASSWORD_REGEX, min_length=6, max_length=32)
    repeat_password: str = Field(pattern=PASSWORD_REGEX, min_length=6, max_length=32)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return strip_and_lower(v)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class SignInRequest(BaseModel):
    login: str
    password: str = Field(min_length=6)

    @field_validator("login")
    @classmethod
    def validate_login(cls, v: str) -> str:
        return strip_and_lower(v)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class OAuthConfirmRequest(BaseModel):
    provider: str
    code: str
    user_id: UUID | None
