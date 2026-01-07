from uuid import UUID

from pydantic import BaseModel, EmailStr


class TokenRequest(BaseModel):
    token: str


class UserRequest(BaseModel):
    user_id: UUID


class UserBulkRequest(BaseModel):
    user_ids: list[UUID]


class UsernameRequest(BaseModel):
    username: str


class UsernameUpdateRequest(BaseModel):
    username: str
    user_id: UUID


class EmailRequest(BaseModel):
    email: EmailStr


class EmailVerifyRequest(BaseModel):
    email: EmailStr
    token: str


class PasswordConfirmRequest(BaseModel):
    email: EmailStr
    token: str
    auth_token: str | None
    password: str
    repeat_password: str


class SignupConfirmRequest(BaseModel):
    email: EmailStr
    username: str
    token: str
    password: str
    repeat_password: str


class SignInRequest(BaseModel):
    login: str
    password: str


class OAuthConfirmRequest(BaseModel):
    provider: str
    code: str
    user_id: UUID | None
