from src.env_config import env
from redis.asyncio import Redis
from typing import Optional

class RedisRepository:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def _get_by_key(self, key: str) -> dict | None:
        response = await self.redis.hgetall(key)
        if not response:
            return None
        return {k.decode() if isinstance(k, bytes) else k: v.decode() if isinstance(v, bytes) else v for k, v in response.items()}

    async def get_user_by_id(self, user_id: int) -> dict | None:
        hash_value = f"user-{user_id}"
        return await self._get_by_key(hash_value)

