from fastapi import Depends, Request, Response
from fastapi_controllers import Controller, get, post, put
from ..models import UserModel, UpdateResponse, StatusResponse, UpdateUserRequest, SignInRequest
from ..exceptions import AlreadyAuthorizedException

from typing import Annotated
from ..service import UserService
from src.dependency import get_user_service


class AuthController(Controller):
    prefix = "/auth"
    tags = ["auth"]

    def __init__(self, user_service: Annotated[UserService, Depends(get_user_service)]) -> None:
        super().__init__()
        self.user_service = user_service

    @get("/user", response_model=UserModel)
    async def get_user_info(self, request: Request) -> UserModel:
        user_uuid = await self.user_service.get_user_id(request.cookies.get("token"))
        return await self.user_service.get_user_info(user_uuid)

    @put("/user", response_model=UpdateResponse)
    async def update_username(self, data: UpdateUserRequest, request: Request) -> UpdateResponse:
        user_uuid = await self.user_service.get_user_id(request.cookies.get("token"))
        ok = await self.user_service.update_username(user_uuid, data.username)
        return UpdateResponse(updated=ok)

    @post("/signin", response_model=StatusResponse)
    async def sign_in(self, request: Request, data: SignInRequest, response: Response) -> StatusResponse:
        if request.cookies.get("token", None):
            raise AlreadyAuthorizedException()
        token = await self.user_service.sign_in(data.login, data.password)
        response.set_cookie("token", token, httponly=True)
        return StatusResponse()

    @post("/signout", response_model=StatusResponse)
    async def sign_out(self, request: Request, response: Response) -> StatusResponse:
        await self.user_service.sign_out(request.cookies.get("token"))
        response.delete_cookie("token")
        return StatusResponse()
