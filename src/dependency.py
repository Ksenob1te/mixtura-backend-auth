from faststream import Context, Depends

from src.domain.service.auth import AuthService
from src.domain.service.oauth import OAuthService
from .infra.postgre import DatabaseSessionManager, ProviderRepository, UserRepository
from .infra.redis import RedisSessionManager, RedisRepository
from .infra.smtp import SMTPRepository, SMTPManager
from .domain.service import UserService, MailService

from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from aiosmtplib import SMTP

import logging

logger = logging.getLogger(__name__)


async def get_db_session(session_manager: Annotated[DatabaseSessionManager, Context()]):
    async with session_manager.session() as session:
        yield session


async def get_redis_session(redis_engine: Annotated[RedisSessionManager, Context()]):
    async with redis_engine.client() as redis:
        yield redis


async def get_smtp_session(smtp_engine: Annotated[SMTPManager, Context()]):
    async with smtp_engine.client() as smtp:
        yield smtp


async def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    return UserRepository(session)


async def get_provider_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    return ProviderRepository(session)


async def get_redis_repository(redis: Annotated[Redis, Depends(get_redis_session)]):
    return RedisRepository(redis)


async def get_smtp_repository(smtp: Annotated[SMTP, Depends(get_smtp_session)]):
    return SMTPRepository(smtp)


async def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    provider_repo: Annotated[ProviderRepository, Depends(get_provider_repository)],
    redis_repo: Annotated[RedisRepository, Depends(get_redis_repository)],
):
    return UserService(user_repo, provider_repo, redis_repo)


async def get_mail_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    redis_repo: Annotated[RedisRepository, Depends(get_redis_repository)],
    smtp_repo: Annotated[SMTPRepository, Depends(get_smtp_repository)],
):
    return MailService(smtp_repo, redis_repo, user_repo)


async def get_auth_service():
    return AuthService()


async def get_oauth_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    provider_repo: Annotated[ProviderRepository, Depends(get_provider_repository)],
    redis_repo: Annotated[RedisRepository, Depends(get_redis_repository)],
):
    return OAuthService(user_repo, provider_repo, redis_repo)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
MailServiceDep = Annotated[MailService, Depends(get_mail_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
OAuthServiceDep = Annotated[OAuthService, Depends(get_oauth_service)]
