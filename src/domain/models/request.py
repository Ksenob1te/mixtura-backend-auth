from pydantic import BaseModel, Field, field_validator, EmailStr


def strip_and_lower(v: object) -> str:
    return str(v).strip().lower()


class UpdateUserRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)


class ResetPasswordRequest(BaseModel):
    email: EmailStr = None

    @field_validator("email")
    @classmethod
    def validate_login(cls, v: str) -> str:
        return strip_and_lower(v)


class ResetPasswordVerify(BaseModel):
    email: EmailStr = None
    token: str

    @field_validator("email")
    @classmethod
    def validate_login(cls, v: str) -> str:
        return strip_and_lower(v)


class ResetPasswordConfirm(BaseModel):
    email: EmailStr = None
    token: str
    password: str
    repeat_password: str

    @field_validator("email")
    @classmethod
    def validate_login(cls, v: str) -> str:
        return strip_and_lower(v)


class SignInRequest(BaseModel):
    login: str
    password: str

    @field_validator("login")
    @classmethod
    def validate_login(cls, v: str) -> str:
        return strip_and_lower(v)

