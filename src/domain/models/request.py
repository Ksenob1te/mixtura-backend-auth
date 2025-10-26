from enum import Enum
from pydantic import BaseModel, Field, field_validator, EmailStr

from src.domain.constants import PASSWORD_REGEX, USERNAME_REGEX


class UsernameRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=USERNAME_REGEX)


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
    password: str = Field(pattern=PASSWORD_REGEX, min_length=6, max_length=32)
    repeat_password: str = Field(pattern=PASSWORD_REGEX, min_length=6, max_length=32)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return strip_and_lower(v)


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


class SignInRequest(BaseModel):
    login: str
    password: str = Field(min_length=6)

    @field_validator("login")
    @classmethod
    def validate_login(cls, v: str) -> str:
        return strip_and_lower(v)


class OAuthConfirm(BaseModel):
    provider: str
    code: str
