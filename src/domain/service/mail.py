from src.infra.postgre import ProviderRepository, UserRepository, Provider, User
from src.infra.redis import RedisRepository
from src.infra.smtp import SMTPRepository
import random
import string
from typing import Optional, List
from uuid import UUID, uuid4
from email_validator import validate_email, EmailNotValidError

from ..models import UserModel
from ..exceptions import NotAuthorizedException, InvalidCredentialsException


class MailService:
    def __init__(self, smtp_repo: SMTPRepository, redis_repo: RedisRepository):
        self.redis_repo = redis_repo
        self.smtp_repo = smtp_repo

    async def request_access(self, email: str) -> None:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


        await self.smtp_repo.send_access_request_email(email, token)
