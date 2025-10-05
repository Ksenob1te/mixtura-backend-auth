from pydantic import BaseModel, Field


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


class Provider(BaseModel):
    icon_url: str
    id: str
    display_name: str
    redirect_uri: str
    use_in_auth: bool
    limit: int


class Providers(BaseModel):
    email_enabled: bool
    oauth_providers: list[Provider]
