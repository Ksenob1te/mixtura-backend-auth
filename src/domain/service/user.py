from src.infra.postgre import ProviderRepository, UserRepository, Provider, User
from src.infra.redis import RedisRepository
from typing import Optional, List
from uuid import UUID, uuid4
from email_validator import validate_email, EmailNotValidError

from ..models import UserModel
from ..exceptions import NotAuthorizedException, InvalidCredentialsException


class UserService:
    def __init__(self, user_repo: UserRepository, provider_repo: ProviderRepository, redis_repo: RedisRepository):
        self.user_repo = user_repo
        self.provider_repo = provider_repo
        self.redis_repo = redis_repo

    async def validate_user_token(self, token: Optional[str]) -> bool:
        if not token:
            return False
        session_data = await self.redis_repo.get_user_by_cookie(token)
        return session_data is not None

    async def get_user_id(self, token: Optional[str]) -> UUID:
        session_data = await self.redis_repo.get_user_by_cookie(token)
        if not session_data:
            raise NotAuthorizedException()
        return UUID(session_data)

    async def get_user_id_by_email(self, email: str) -> UUID | None:
        user: User | None = await self.user_repo.get_by_email(email)
        if not user:
            return None
        return user.id

    async def get_user_info(self, user_id: UUID) -> UserModel | None:
        user_model: User = await self.user_repo.get_by_id(user_id)
        user_pydantic = UserModel.model_validate(user_model)
        return user_pydantic

    async def update_username(self, user_id: UUID, new_username: str) -> bool:
        return await self.user_repo.change_username(user_id, new_username)

    async def change_password(self, user_id: UUID, new_password: str) -> bool:
        return await self.user_repo.change_password(user_id, new_password)

    async def sign_in(self, login: str, password: str) -> str:
        try:
            validate_email(login, check_deliverability=False, globally_deliverable=False)
            user: User | None = await self.user_repo.get_by_email(login)
        except EmailNotValidError:
            user: User | None = await self.user_repo.get_by_username(login)
        if not user or not await self.user_repo.check_password(user, password):
            raise InvalidCredentialsException()
        token = uuid4().hex
        await self.redis_repo.set_user_cookie(token, user.id)
        return token

    async def sign_out(self, token: str) -> None:
        await self.redis_repo.remove_user_cookie(token)

