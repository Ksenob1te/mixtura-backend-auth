from contextlib import asynccontextmanager

from faststream import ContextRepo, ExceptionMiddleware, FastStream
from faststream.rabbit import RabbitBroker

import src.domain.api as api
from src.env_config import env
from src.infra.postgre import DatabaseSessionManager
from src.infra.redis import RedisSessionManager
from src.infra.smtp import SMTPManager

from .exceptions import DomainException
from .models.response import ErrorResponse, ResponseMessage

exc_middleware = ExceptionMiddleware()


@exc_middleware.add_handler(DomainException, publish=True)
def error_handler(exc: DomainException) -> ResponseMessage[ErrorResponse]:
    return ResponseMessage(
        status=exc.status_code, message=ErrorResponse(message=exc.message)
    )


broker = RabbitBroker(env.rabbit.url, middlewares=[exc_middleware])

broker.include_router(api.router)


@asynccontextmanager
async def lifespan(context: ContextRepo):
    session_manager = DatabaseSessionManager(env.postgres.url)
    redis_engine = RedisSessionManager(env.redis.url)
    smtp_engine = SMTPManager(
        env.smtp.host, env.smtp.port, env.smtp.user, env.smtp.password
    )

    context.set_global("session_manager", session_manager)
    context.set_global("redis_engine", redis_engine)
    context.set_global("smtp_engine", smtp_engine)

    yield

    if await session_manager.opened:
        await session_manager.close()
    if await redis_engine.opened:
        await redis_engine.close()


app = FastStream(broker, lifespan=lifespan)
