from typing import List, Dict
from pydantic import BaseModel, Field, HttpUrl
from pydantic_settings import BaseSettings
import yaml
from pathlib import Path

CONFIG_PATH = Path("./.local/config.yaml")

class OAuthProviderConfig(BaseModel):
    display_name: str
    icon_url: str
    auth_url: str
    token_url: str
    user_url: str
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: List[str] = []
    use_in_auth: bool = False
    enabled: bool = False

class ProvidersConfig(BaseSettings):
    email_enabled: bool = True
    oauth_providers: Dict[str, OAuthProviderConfig] = Field(
        default_factory=lambda: {
            "discord": OAuthProviderConfig(
                display_name="Discord",
                icon_url="",
                auth_url="https://discord.com/api/oauth2/authorize",
                token_url="https://discord.com/api/oauth2/token",
                user_url="https://discord.com/api/users/@me",
                client_id="your_discord_client_id",
                client_secret="your_discord_client_secret",
                redirect_uri="https://yourapp.com/oauth/callback/discord",
                scopes=["identify", "email"]
            ),
            "twitch": OAuthProviderConfig(
                display_name="Twitch",
                icon_url="",
                auth_url="https://id.twitch.tv/oauth2/authorize",
                token_url="https://id.twitch.tv/oauth2/token",
                user_url="https://api.twitch.tv/helix/users",
                client_id="your_twitch_client_id",
                client_secret="your_twitch_client_secret",
                redirect_uri="https://yourapp.com/oauth/callback/twitch",
                scopes=["user:read:email"]
            ),
        }
    )
    @classmethod
    def load_or_create(cls, path: Path = CONFIG_PATH) -> "ProvidersConfig":
        if path.exists():
            # Загружаем из YAML
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(stream=f) or {}
            return cls(**data["config"])
        else:
            config = cls()
            # Сохраняем YAML
            with open(path, "w", encoding="utf-8") as f:
                yaml.safe_dump({"config": config.model_dump()}, f, sort_keys=False)
            print(f"Создан новый конфиг: {path}")
            return config

PROVIDERS = ProvidersConfig.load_or_create()