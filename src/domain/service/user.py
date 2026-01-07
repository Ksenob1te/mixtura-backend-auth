from src.infra.postgre import ProviderRepository, UserRepository, User
from src.infra.redis import RedisRepository
from uuid import UUID, uuid4
from email_validator import validate_email, EmailNotValidError

from ..exceptions import NotAuthorizedException, InvalidCredentialsException, PasswordsDontMatchException, \
    UsernameAlreadyTakenException, EmailFormatException


class UserService:
    def __init__(self, user_repo: UserRepository, provider_repo: ProviderRepository, redis_repo: RedisRepository):
        self.user_repo = user_repo
        self.provider_repo = provider_repo
        self.redis_repo = redis_repo

    async def validate_user_token(self, token: str | None) -> bool:
        if not token:
            return False
        session_data = await self.redis_repo.get_user_by_cookie(token)
        return session_data is not None

    async def revoke_tokens(self, user_id: UUID, exclude_token: None | str | list[str] = None) -> None:
        await self.redis_repo.revoke_all_user_cookies(user_id, exclude_token)

    async def get_user_id(self, token: str | None) -> UUID:
        if not token:
            raise NotAuthorizedException()
        session_data = await self.redis_repo.get_user_by_cookie(token)
        if not session_data:
            raise NotAuthorizedException()
        return UUID(session_data)

    async def get_user_id_by_email(self, email: str) -> UUID | None:
        user = await self.user_repo.get_by_email(email)
        return user.id if user else None

    async def get_user_id_by_email_bulk(self, emails: list[str]) -> dict[str, UUID]:
        users = await self.user_repo.get_by_email_bulk(emails)
        return {user.email: user.id for user in users if user.email is not None}

    async def get_user_id_by_username(self, username: str) -> UUID | None:
        user = await self.user_repo.get_by_username(username)
        return user.id if user else None

    async def get_user_id_by_username_bulk(self, usernames: list[str]) -> dict[str, UUID]:
        users = await self.user_repo.get_by_username_bulk(usernames)
        return {user.username: user.id for user in users}

    async def get_user_field(self, user_id: UUID) -> User | None:
        user_model = await self.user_repo.get_by_id(user_id)
        return user_model

    async def get_user_field_bulk(self, user_ids: list[UUID]) -> dict[UUID, User]:
        users = await self.user_repo.get_by_id_bulk(user_ids)
        return {user.id: user for user in users}

    async def username_available(self, username: str) -> bool:
        user = await self.user_repo.get_by_username(username)
        return user is None

    async def change_username(self, user_id: UUID, new_username: str) -> bool:
        existing_user_id = await self.get_user_id_by_username(new_username)
        if existing_user_id is not None and existing_user_id != user_id:
            raise UsernameAlreadyTakenException()
        return await self.user_repo.change_username(user_id, new_username)

    async def change_password(self, user_id: UUID, password: str, password_repeat: str) -> bool:
        if password != password_repeat:
            raise PasswordsDontMatchException()
        return await self.user_repo.change_password(user_id, password)

    async def sign_in(self, login: str, password: str) -> str:
        try:
            validate_email(login, check_deliverability=False, globally_deliverable=False)
            user = await self.user_repo.get_by_email(login)
        except EmailNotValidError:
            user = await self.user_repo.get_by_username(login)
        if not (user and await self.user_repo.check_password(user, password)):
            raise InvalidCredentialsException()
        token = uuid4().hex
        await self.redis_repo.set_user_cookie(token, user.id)
        return token

    async def sign_out(self, token: str | None) -> None:
        if token is None:
            raise NotAuthorizedException()
        await self.redis_repo.remove_user_cookie(token)

    async def sign_up(self, username: str, email: str, password: str, password_repeat: str) -> UUID | None:
        try:
            validate_email(email, check_deliverability=False)
        except EmailNotValidError:
            raise EmailFormatException()
        if password != password_repeat:
            raise PasswordsDontMatchException()
        user_id = await self.get_user_id_by_username(username)
        if user_id is not None:
            raise UsernameAlreadyTakenException()
        user_id = await self.get_user_id_by_email(email)
        if user_id:
            return None
        user_field = await self.user_repo.create_user(username=username, email=email, password=password)
        return user_field.id if user_field else None
