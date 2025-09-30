from enum import Enum
from pydantic import BaseModel, Field, field_validator, EmailStr


class UpdateUserRequest(BaseModel):
    username: str = Field(min_length=4, max_length=16)


def strip_and_lower(v: object) -> str:
    return str(v).strip().lower()


class ResetPasswordRequest(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def validate_login(cls, v: str) -> str:
        return strip_and_lower(v)


class ResetPasswordVerify(BaseModel):
    email: EmailStr
    token: str

    @field_validator("email")
    @classmethod
    def validate_login(cls, v: str) -> str:
        return strip_and_lower(v)


class ResetPasswordConfirm(BaseModel):
    email: EmailStr
    token: str
    password: str
    repeat_password: str

    @field_validator("email")
    @classmethod
    def validate_login(cls, v: str) -> str:
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
