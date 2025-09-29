from pydantic import BaseModel, Field, field_validator


class UpdateUserRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)


def strip_and_lower(v: object) -> str:
    return str(v).strip().lower()


class SignInRequest(BaseModel):
    login: str
    password: str = Field(min_length=1)

    @field_validator("login")
    @classmethod
    def validate_login(cls, v: str) -> str:
        return strip_and_lower(v)

