from src.infra.postgre import ProviderRepository, UserRepository, UserProvider, User
from src.infra.redis import RedisRepository
from src.infra.smtp import SMTPRepository
import random
import string
from typing import Optional, List
from uuid import UUID, uuid4
from email_validator import validate_email, EmailNotValidError

from ..models import UserModel
from ..exceptions import ExceedRetryLimitException


class MailService:
    def __init__(self, smtp_repo: SMTPRepository, redis_repo: RedisRepository, user_repo: UserRepository):
        self.user_repo = user_repo
        self.redis_repo = redis_repo
        self.smtp_repo = smtp_repo

    async def request_access(self, email: str) -> None:
        code = ''.join(random.choices(string.digits, k=6))
        await self.redis_repo.assign_email_code(email, code)
        await self.smtp_repo.send_code(email, code)

    async def verify_access(self, email: str, code: str) -> bool:
        stored_code = await self.redis_repo.get_email_code(email)
        if stored_code is None:
            return False
        counter = await self.redis_repo.get_email_counter(email)
        if counter >= 3:
            raise ExceedRetryLimitException()
        if stored_code and stored_code == code:
            return True
        await self.redis_repo.increment_email_counter(email)
        return False

    async def remove_access_code(self, email: str) -> None:
        await self.redis_repo.remove_email_code(email)
