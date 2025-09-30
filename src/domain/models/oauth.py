from enum import Enum

from pydantic import BaseModel


class Provider(Enum, str):
    DISCORD = "discord"
    TWITCH = "twitch"

class OAuthRequest(BaseModel):
    provider: Provider

class OAuthConfirm(BaseModel):
    provider: Provider
    code: str

class OAuthRedirect(BaseModel):
    provider: Provider
    redirect_url: str
