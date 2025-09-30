from fastapi import Depends, Request, Response
from fastapi_controllers import Controller, get, post, put

from src.domain.models.response import Provider, Providers
from src.domain.service.auth import AuthService
from src.domain.service.oauth import OAuthService
from src.providers_config import PROVIDERS
from ..models import *
from ..exceptions import AlreadyAuthorizedException, PasswordsDontMatchException

from typing import Annotated
from ..service import UserService, MailService
from src.dependency import get_auth_service, get_oauth_service, get_user_service, get_mail_service


class AuthController(Controller):
    prefix = "/auth"
    tags = ["auth"]

    def __init__(self,
                 user_service: Annotated[UserService, Depends(get_user_service)],
                 mail_service: Annotated[MailService, Depends(get_mail_service)],
                 auth_service: Annotated[AuthService, Depends(get_auth_service)],
                 oauth_service: Annotated[OAuthService, Depends(get_oauth_service)]) -> None:
        super().__init__()
        self.user_service = user_service
        self.mail_service = mail_service
        self.auth_service = auth_service
        self.oauth_service = oauth_service

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
        if self.user_service.validate_user_token(request.cookies.get("token", None)):
            raise AlreadyAuthorizedException()
        token = await self.user_service.sign_in(data.login, data.password)
        response.set_cookie("token", token, httponly=True)
        return StatusResponse()

    @post("/signout", response_model=StatusResponse)
    async def sign_out(self, request: Request, response: Response) -> StatusResponse:
        await self.user_service.sign_out(request.cookies.get("token"))
        response.delete_cookie("token")
        return StatusResponse()

    @post("/reset", response_model=StatusResponse)
    async def reset(self, request: ResetPasswordRequest) -> StatusResponse:
        user_id = await self.user_service.get_user_id_by_email(str(request.email))
        if user_id:
            await self.mail_service.request_access(str(request.email))
        return StatusResponse()

    @post("/reset/verify", response_model=VerifyResponse)
    async def verify_reset(self, request: ResetPasswordVerify) -> VerifyResponse:
        verified = await self.mail_service.verify_access(str(request.email), request.token)
        return VerifyResponse(verified=verified)

    @post("/reset/confirm", response_model=VerifyResponse)
    async def confirm_reset(self, request: ResetPasswordConfirm) -> VerifyResponse:
        if request.password != request.repeat_password:
            raise PasswordsDontMatchException()
        verified = await self.mail_service.verify_access(str(request.email), request.token)
        if verified:
            user_id = await self.user_service.get_user_id_by_email(str(request.email))
            await self.mail_service.remove_access_code(str(request.email))
            await self.user_service.change_password(user_id, request.password)
            # TODO: add session removal here
        return VerifyResponse(verified=verified)

    @get("/providers", response_model=Providers)
    async def providers(self):
        return self.auth_service.get_providers()
    
    @post("/callback")
    async def callback(self, req: OAuthConfirm, request: Request):
        pass