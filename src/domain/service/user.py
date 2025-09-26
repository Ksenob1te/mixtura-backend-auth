# from ..exceptions import LogInAnswer, LogInRequest, SignUpRequest

from src.infra.postgre import ProviderRepository, UserRepository, Provider, User
from src.infra.redis import RedisRepository
from fastapi import Request
from typing import Optional, List
from uuid import UUID

from ..models import UserModel
from ..exceptions import NotAuthorizedException


class UserService:
    def __init__(self, user_repo: UserRepository, provider_repo: ProviderRepository, redis_repo: RedisRepository):
        self.user_repo = user_repo
        self.provider_repo = provider_repo
        self.redis_repo = redis_repo

    async def get_user_id(self, token: Optional[str]) -> UUID:
        session_data = await self.redis_repo.get_user_by_cookie(token)
        if not session_data:
            raise NotAuthorizedException()
        return UUID(session_data)

    async def get_user_info(self, user_id: UUID) -> UserModel | None:
        user_model: User = await self.user_repo.get_by_id(user_id)
        user_pydantic = UserModel.model_validate(user_model)
        return user_pydantic


