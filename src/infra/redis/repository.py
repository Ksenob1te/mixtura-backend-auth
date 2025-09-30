from src.env_config import env
from redis.asyncio import Redis
from typing import Optional
from datetime import timedelta
from uuid import UUID


class RedisRepository:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def _get_dict_by_key(self, key: str) -> dict | None:
        response = await self.redis.hgetall(key)  # type: ignore
        if not response:
            return None
        return {k.decode() if isinstance(k, bytes) else k: v.decode() if isinstance(v, bytes) else v for k, v in
                response.items()}

    async def _get_element_by_key(self, key: str) -> str | None:
        response = await self.redis.get(key)
        if not response:
            return None
        return response.decode() if isinstance(response, bytes) else response

    async def get_user_by_cookie(self, cookie: str) -> str | None:
        hash_value = f"cookie::{cookie}"
        return await self._get_element_by_key(hash_value)

    async def _extend_user_set(self, user_id: UUID, token: str) -> None:
        key = f"user::session::{user_id}"
        await self.redis.sadd(key, token)  # type: ignore

    async def _remove_from_user_set(self, user_id: UUID, token: str) -> None:
        key = f"user::session::{user_id}"
        await self.redis.srem(key, token)  # type: ignore

    async def set_user_cookie(self, token: str, user_id: UUID, expire: timedelta = timedelta(days=30)) -> None:
        key = f"cookie::{token}"
        await self.redis.set(key, str(user_id), ex=expire)
        await self._extend_user_set(user_id, token)

    async def remove_user_cookie(self, token: str) -> None:
        user_uuid = await self.get_user_by_cookie(token)
        if not user_uuid:
            return
        key = f"cookie::{token}"
        await self.redis.delete(key)
        await self._remove_from_user_set(UUID(user_uuid), token)

    async def get_all_user_cookies(self, user_id: UUID) -> list[str]:
        key = f"user::session::{user_id}"
        tokens = await self.redis.smembers(key)  # type: ignore
        if not tokens:
            return []
        return [token.decode() if isinstance(token, bytes) else token for token in tokens]

    async def revoke_all_user_cookies(self, user_id: UUID, exclude_token: None | str | list[str] = None) -> None:
        key = f"user::session::{user_id}"
        tokens = await self.redis.smembers(key)  # type: ignore
        if not tokens:
            return
        tokens_to_delete = []
        for token in tokens:
            token_str = token.decode() if isinstance(token, bytes) else token
            if (
                    exclude_token is None or
                    (isinstance(exclude_token, str) and token_str != exclude_token) or
                    (isinstance(exclude_token, list) and token_str not in exclude_token)
            ):
                tokens_to_delete.append(token_str)
        if tokens_to_delete:
            await self.redis.delete(*[f"cookie::{token}" for token in tokens_to_delete])
            if exclude_token is None:
                await self.redis.delete(key)
            else:
                await self.redis.srem(key, *tokens_to_delete)  # type: ignore

    async def get_email_code(self, email: str) -> str | None:
        key = f"email::verify::{email}"
        result = await self._get_dict_by_key(key)
        return result.get("code") if result else None

    async def get_email_counter(self, email: str) -> int | None:
        key = f"email::verify::{email}"
        result = await self._get_dict_by_key(key)
        count = result.get("count") if result else None
        return int(count) if count and count.isdigit() else 0

    async def increment_email_counter(self, email: str) -> int:
        key = f"email::verify::{email}"
        return await self.redis.hincrby(key, "count", 1)  # type: ignore

    async def assign_email_code(self, email: str, code: str, expire: timedelta = timedelta(minutes=10)) -> None:
        key = f"email::verify::{email}"

        await self.redis.hset(key, mapping={"code": code, "count": 0})  # type: ignore
        await self.redis.expire(key, expire)

    async def remove_email_code(self, email: str) -> None:
        key = f"email::verify::{email}"
        await self.redis.delete(key)
