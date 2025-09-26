# from backend.dependencies import UserServiceDepends
# from backend.utils import GetDBSession, GetOptionalUser, GetRedisClient, GetUser
# from domain.services.user.service import UserService
from fastapi import Response, Depends, Request
from fastapi_controllers import Controller, get, post
from ..models import UserModel

from typing import Annotated
from ..service import UserService
from src.dependency import get_user_service
# from postgre_module.repository.user_repository import UserRepository
# from redis_module.repository import RedisRepository
# from domain.services.user.models import LogInRequest as DomainLogInRequest, SignUpRequest as DomainSignUpRequest
# from settings import APP_SETTINGS


class AuthController(Controller):
    prefix = "/auth"
    tags = ["auth"]

    def __init__(self, user_service: Annotated[UserService, Depends(get_user_service)]) -> None:
        super().__init__()
        self.user_service = user_service

    @get("", response_model=UserModel)
    async def get_user_info(self, request: Request) -> UserModel:
        user_uuid = await self.user_service.get_user_id(request.cookies.get("token"))
        return await self.user_service.get_user_info(user_uuid)

    @post("/login")
    async def login(self, data: LogInRequest, response: Response):
        result = await self.user_service.login(
            DomainLogInRequest(
                data.username,
                data.password)
        )
        response.set_cookie("token",
                            result.token,
                            max_age=APP_SETTINGS.ttl.auth_token_expire,
                            httponly=True)
        return {"message": "OK"}

    @post("/logout")
    async def logout(self, user: GetUser, response: Response):
        await self.user_service.logout(user.token)
        response.delete_cookie("token")
        return {"message": "OK"}

    @post("/registration")
    async def registration(self, data: SignUpRequest):
        await self.user_service.signup(DomainSignUpRequest(
            data.username,
            data.password,
            data.repeat_password
        ))
        return {"message": "OK"}
