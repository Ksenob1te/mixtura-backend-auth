from fastapi import Depends, Request, Response
from fastapi_controllers import Controller, get, post, put

from src.providers_config import PROVIDERS

from ..service.auth import AuthService
from ..service.oauth import OAuthService
from ..service import UserService, MailService
from ..models import *
from ..exceptions import AlreadyAuthorizedException, InternalLogicException, NotAuthorizedException

from src.infra.postgre import User

from typing import Annotated
from src.dependency import get_auth_service, get_oauth_service, get_user_service, get_mail_service

import logging


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
        self.logger = logging.getLogger(__name__)
        self.auth_service = auth_service
        self.oauth_service = oauth_service

    @get("/user", response_model=UserModel)
    async def get_user_info(self, request: Request) -> User:
        user_uuid = await self.user_service.get_user_id(request.cookies.get("token"))
        user_field = await self.user_service.get_user_field(user_uuid)
        if user_field is None:
            self.logger.warning(
                "User authorized, but not found in DB, id=%s", user_uuid)
            raise InternalLogicException("User not found")
        return user_field

    @put("/user", response_model=UpdateResponse)
    # todo: do patch here instead of put
    async def update_username(self, request: Request, data: UsernameRequest) -> UpdateResponse:
        # todo: add regex username validation
        user_uuid = await self.user_service.get_user_id(request.cookies.get("token"))
        ok = await self.user_service.change_username(user_uuid, data.username)
        return UpdateResponse(updated=ok)

    @post("/signin", response_model=StatusResponse)
    async def sign_in(self, request: Request, data: SignInRequest, response: Response) -> StatusResponse:
        if await self.user_service.validate_user_token(request.cookies.get("token", None)):
            raise AlreadyAuthorizedException()
        token = await self.user_service.sign_in(data.login, data.password)
        response.set_cookie("token", token, httponly=True)
        return StatusResponse()

    @post("/signout", response_model=StatusResponse)
    async def sign_out(self, request: Request, response: Response) -> StatusResponse:
        response.delete_cookie("token")
        await self.user_service.sign_out(request.cookies.get("token", None))
        return StatusResponse()

    @post("/reset", response_model=StatusResponse)
    async def reset(self, data: EmailRequest) -> StatusResponse:
        user_id = await self.user_service.get_user_id_by_email(str(data.email))
        if user_id:
            await self.mail_service.request_access(str(data.email))
        return StatusResponse()

    @post("/reset/verify", response_model=VerifyResponse)
    async def verify_reset(self, data: EmailVerifyRequest) -> VerifyResponse:
        verified = await self.mail_service.verify_access(str(data.email), data.token)
        return VerifyResponse(verified=verified)

    @post("/reset/confirm", response_model=VerifyResponse)
    async def confirm_reset(self, request: Request, data: PasswordConfirmRequest) -> VerifyResponse:
        # todo: add regex password validation
        verified = await self.mail_service.verify_access(str(data.email), data.token)
        if verified:
            user_id = await self.user_service.get_user_id_by_email(str(data.email))
            if user_id is None:
                return VerifyResponse(verified=False)
            await self.user_service.change_password(user_id, data.password, data.repeat_password)
            await self.user_service.revoke_tokens(user_id, exclude_token=request.cookies.get("token", None))
            await self.mail_service.remove_access_code(str(data.email))
        return VerifyResponse(verified=verified)

    @post("/signup", response_model=StatusResponse)
    async def sign_up(self, data: EmailRequest) -> StatusResponse:
        if not PROVIDERS.email_enabled:
            raise InternalLogicException("Email sign up is disabled")
        existing_user_id = await self.user_service.get_user_id_by_email(str(data.email))
        if not existing_user_id:
            await self.mail_service.request_access(str(data.email))
        return StatusResponse()

    @post("/signup/verify", response_model=VerifyResponse)
    async def verify_sign_up(self, data: EmailVerifyRequest) -> VerifyResponse:
        if not PROVIDERS.email_enabled:
            raise InternalLogicException("Email sign up is disabled")
        verified = await self.mail_service.verify_access(str(data.email), data.token)
        return VerifyResponse(verified=verified)

    @post("/signup/confirm", response_model=VerifyResponse)
    # todo: add regex password validation
    async def confirm_sign_up(self, request: Request, data: SignupConfirmRequest, response: Response) -> VerifyResponse:
        if not PROVIDERS.email_enabled:
            raise InternalLogicException("Email sign up is disabled")
        verified = await self.mail_service.verify_access(str(data.email), data.token)
        if verified:
            user_id = await self.user_service.sign_up(
                data.username,
                str(data.email),
                data.password,
                data.repeat_password
            )
            if not user_id:
                return VerifyResponse(verified=False)
            await self.mail_service.remove_access_code(str(data.email))
            if not await self.user_service.validate_user_token(request.cookies.get("token", None)):
                token = await self.user_service.sign_in(str(data.email), data.password)
                response.set_cookie("token", token, httponly=True)
        return VerifyResponse(verified=verified)

    @get("/providers", response_model=Providers)
    async def providers(self):
        return self.auth_service.get_providers()

    @post("/callback")
    async def callback(self, req: OAuthConfirm, request: Request, response: Response):
        try:
            user_uuid = await self.user_service.get_user_id(request.cookies.get("token"))
            await self.oauth_service.add_integration(user_uuid, req.provider, req.code)
        except NotAuthorizedException:
            token = await self.oauth_service.authorize(req.provider, req.code)
            response.set_cookie("token", token, httponly=True)
        return StatusResponse()

    @post("/check", response_model=BusyResponse)
    async def check(self, data: UsernameRequest) -> BusyResponse:
        return BusyResponse(busy=not await self.user_service.username_available(data.username))
