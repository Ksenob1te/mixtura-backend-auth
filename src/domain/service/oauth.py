import random
from uuid import UUID, uuid4
import httpx
from typing import Any

from src.domain.exceptions import InternalLogicException, NotEnabledForAuthProviderException, NotFoundProviderException, WrongOAuthCodeException
from src.infra.postgre.repo.provider import ProviderRepository
from src.infra.postgre.repo.user import UserRepository
from src.infra.redis.repository import RedisRepository
from src.providers_config import PROVIDERS


class OAuthService:
    def __init__(self,
                 user_repository: UserRepository,
                 provider_repository: ProviderRepository,
                 redis_repository: RedisRepository) -> None:
        # маппинг функций нормализации профиля
        self.user_parsers = {
            "discord": self._parse_discord_user,
            "twitch": self._parse_twitch_user,
            "battlenet": self._parse_battlenet_user,
        }

        self.user_repository = user_repository
        self.provider_repository = provider_repository
        self.redis_repository = redis_repository

    async def authorize(self, provider: str, code: str) -> str:
        if provider not in PROVIDERS.oauth_providers:
            raise NotFoundProviderException()
        if PROVIDERS.oauth_providers[provider].enabled is False:
            raise NotFoundProviderException()
        if PROVIDERS.oauth_providers[provider].use_in_auth is False:
            raise NotEnabledForAuthProviderException()

        provider_info = await self.process_callback(provider, code)
        user_provider = await self.provider_repository.get_by_client_and_provider_name(provider_info["id"], provider)
        if user_provider is not None:
            token = uuid4().hex
            await self.redis_repository.set_user_cookie(token, user_provider.user.id)
            return token

        user = await self.user_repository.create_user(provider_info["username"] + str(random.randint(100000, 999999)), None, "")
        await self.provider_repository.create_provider(provider, provider_info["id"], user.id, provider_info["username"])
        token = uuid4().hex
        await self.redis_repository.set_user_cookie(token, user.id)
        return token

    async def add_integration(self, user_id: UUID, provider: str, code: str) -> bool:
        if provider not in PROVIDERS.oauth_providers:
            raise NotFoundProviderException()
        if PROVIDERS.oauth_providers[provider].enabled is False:
            raise NotFoundProviderException()
        provider_info = await self.process_callback(provider, code)

        user_provider = await self.provider_repository.get_by_client_and_provider_name(provider_info["id"], provider)
        if user_provider is None:
            await self.provider_repository.create_provider(provider, provider_info["id"], user_id, provider_info["username"])
        else:
            return False
        return True

    async def process_callback(self, provider: str, code: str) -> dict[str, Any]:
        config = PROVIDERS.oauth_providers[provider]

        async with httpx.AsyncClient(proxy="http://127.0.0.1:10808") as client:
            # 1. Обмен code -> access_token
            token_resp = await client.post(
                config.token_url,
                data={
                    "client_id": config.client_id,
                    "client_secret": config.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": config.redirect_uri,
                },
                headers={"Accept": "application/json"},
                timeout=10.0,
            )
            token_resp.raise_for_status()
            token_data = token_resp.json()

            access_token = token_data.get("access_token")
            if not access_token:
                raise WrongOAuthCodeException()

            # 2. Запрос профиля
            headers = {"Authorization": f"Bearer {access_token}"}
            if provider == "twitch":
                headers["Client-Id"] = config.client_id

            user_resp = await client.get(config.user_url, headers=headers, timeout=10.0)
            user_resp.raise_for_status()
            user_data = user_resp.json()

        # 3. Нормализуем профиль
        if provider not in self.user_parsers:
            raise InternalLogicException(f"No parser for provider {provider}")

        return self.user_parsers[provider](user_data)

    def _parse_discord_user(self, data: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": data["id"],
            "username": f"{data['username']}"
        }

    def _parse_twitch_user(self, data: dict[str, Any]) -> dict[str, Any]:
        if "data" in data and len(data["data"]) > 0:
            user = data["data"][0]
            return {
                "id": user["id"],
                "username": user["login"]
            }
        return {"id": None, "username": None, "email": None}

    def _parse_battlenet_user(self, data: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": str(data.get("id")),
            "username": data.get("battletag", "")
        }
