from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseMessage(BaseModel, Generic[T]):
    status: int
    message: T


class ErrorResponse(BaseModel):
    message: str


class UpdateResponse(BaseModel):
    status: str = Field(default="ok")
    updated: bool = Field(default=True)


class StatusResponse(BaseModel):
    status: str = Field(default="ok")


class BusyResponse(BaseModel):
    status: str = Field(default="ok")
    busy: bool = Field(default=True)


class VerifyResponse(BaseModel):
    status: str = Field(default="ok")
    verified: bool = Field(default=False)


class ProviderResponse(BaseModel):
    icon_url: str
    id: str
    display_name: str
    redirect_uri: str
    use_in_auth: bool
    limit: int


class ProvidersResponse(BaseModel):
    email_enabled: bool
    oauth_providers: list[ProviderResponse]


class TokenResponse(BaseModel):
    token: str
    expires: int
