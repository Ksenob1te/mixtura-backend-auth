import logging
from uuid import UUID

from faststream import Depends
from faststream.rabbit import RabbitRouter
from pydantic import TypeAdapter

from src.dependency import (
    AuthServiceDep,
    MailServiceDep,
    OAuthServiceDep,
    UserServiceDep,
    get_db_session,
    get_provider_repository,
)
from src.infra.postgre.repo.provider import ProviderRepository
from ..models.request import IntegrationAccountsRequest, UserBulkRequest, UserRequest
from src.providers_config import PROVIDERS

from ..exceptions import InternalLogicException
from ..models import (
    AuthCheckResponse,
    BusyResponse,
    EmailRequest,
    EmailVerifyRequest,
    ErrorResponse,
    OAuthConfirmRequest,
    PasswordConfirmRequest,
    ProvidersResponse,
    ResponseMessage,
    SignInRequest,
    SignupConfirmRequest,
    StatusResponse,
    TokenRequest,
    TokenResponse,
    UpdateResponse,
    UsernameRequest,
    UsernameUpdateRequest,
    UserResponse,
    VerifyResponse,
)

router = RabbitRouter(prefix=".")
logger = logging.getLogger(__name__)


@router.subscriber(queue="get_auth_check")
async def auth_check(
    data: TokenRequest,
    user_service: UserServiceDep,
) -> ResponseMessage[AuthCheckResponse]:
    user_uuid = await user_service.get_user_id(data.token)
    return ResponseMessage(message=AuthCheckResponse(user_id=user_uuid), status=200)


@router.subscriber("get_user_info")
async def get_user_info(
    data: TokenRequest,
    user_service: UserServiceDep,
) -> ResponseMessage[UserResponse | ErrorResponse]:
    user_uuid = await user_service.get_user_id(data.token)
    user_field = await user_service.get_user_field(user_uuid)
    if user_field is None:
        logger.warning("User authorized, but not found in DB, id=%s", user_uuid)
        raise InternalLogicException("User not found")
    return ResponseMessage(message=UserResponse.model_validate(user_field), status=200)

@router.subscriber("get_user")
async def get_user(
    data: UserRequest,
    user_service: UserServiceDep,
) -> ResponseMessage[UserResponse | ErrorResponse]:
    user_field = await user_service.get_user_field(data.user_id)
    if user_field is None:
        logger.warning("User not found in DB, id=%s", data.user_id)
        raise InternalLogicException("User not found")
    return ResponseMessage(message=UserResponse.model_validate(user_field), status=200)

@router.subscriber("get_users.bulk")
async def get_users_bulk(
    data: UserBulkRequest,
    user_service: UserServiceDep,
) -> ResponseMessage[dict[UUID, UserResponse] | ErrorResponse]:
    users_data = await user_service.get_user_field_bulk(data.user_ids)
    ta = TypeAdapter(dict[UUID, UserResponse])
    users = ta.validate_python(users_data)
    return ResponseMessage(message=users, status=200)

@router.subscriber("signin")
async def sign_in(
    data: SignInRequest,
    user_service: UserServiceDep,
) -> ResponseMessage[TokenResponse]:
    token = await user_service.sign_in(data.login, data.password)
    return ResponseMessage(
        message=TokenResponse(token=token, expires=30 * 24 * 60 * 60), status=200
    )


@router.subscriber("update_username")
async def update_username(
    data: UsernameUpdateRequest,
    user_service: UserServiceDep,
) -> ResponseMessage[UpdateResponse]:
    ok = await user_service.change_username(data.user_id, data.username)
    return ResponseMessage(message=UpdateResponse(updated=ok), status=200)


@router.subscriber("signout")
async def sign_out(
    data: TokenRequest,
    user_service: UserServiceDep,
) -> ResponseMessage[StatusResponse]:
    await user_service.sign_out(data.token)
    return ResponseMessage(message=StatusResponse(), status=200)


@router.subscriber("reset")
async def reset(
    data: EmailRequest,
    user_service: UserServiceDep,
    mail_service: MailServiceDep,
) -> ResponseMessage[StatusResponse]:
    user_id = await user_service.get_user_id_by_email(str(data.email))
    if user_id:
        await mail_service.request_access(str(data.email))
    return ResponseMessage(message=StatusResponse(), status=200)


@router.subscriber("reset.verify")
async def verify_reset(
    data: EmailVerifyRequest,
    mail_service: MailServiceDep,
) -> ResponseMessage[VerifyResponse]:
    verified = await mail_service.verify_access(str(data.email), data.token)
    return ResponseMessage(message=VerifyResponse(verified=verified), status=200)


@router.subscriber("reset.confirm")
async def confirm_reset(
    data: PasswordConfirmRequest,
    user_service: UserServiceDep,
    mail_service: MailServiceDep,
) -> ResponseMessage[VerifyResponse]:
    verified = await mail_service.verify_access(str(data.email), data.token)
    if verified:
        user_id = await user_service.get_user_id_by_email(str(data.email))
        if user_id is None:
            return ResponseMessage(message=VerifyResponse(verified=False), status=200)
        await user_service.change_password(user_id, data.password, data.repeat_password)
        await user_service.revoke_tokens(user_id, exclude_token=data.auth_token)
        await mail_service.remove_access_code(data.email)
    return ResponseMessage(message=VerifyResponse(verified=verified), status=200)


@router.subscriber("signup")
async def sign_up(
    data: EmailRequest,
    user_service: UserServiceDep,
    mail_service: MailServiceDep,
) -> ResponseMessage[StatusResponse]:
    if not PROVIDERS.email_enabled:
        raise InternalLogicException("Email sign up is disabled")
    existing_user_id = await user_service.get_user_id_by_email(str(data.email))
    if not existing_user_id:
        await mail_service.request_access(str(data.email))
    return ResponseMessage(message=StatusResponse(), status=200)


@router.subscriber("signup.verify")
async def verify_sign_up(
    data: EmailVerifyRequest,
    mail_service: MailServiceDep,
) -> ResponseMessage[VerifyResponse]:
    if not PROVIDERS.email_enabled:
        raise InternalLogicException("Email sign up is disabled")

    verified = await mail_service.verify_access(str(data.email), data.token)
    return ResponseMessage(message=VerifyResponse(verified=verified), status=200)


@router.subscriber("signup.confirm")
async def confirm_sign_up(
    data: SignupConfirmRequest,
    user_service: UserServiceDep,
    mail_service: MailServiceDep,
) -> ResponseMessage[
    VerifyResponse | TokenResponse
]:  # Returns token on success, or VerifyResponse on failure
    if not PROVIDERS.email_enabled:
        raise InternalLogicException("Email sign up is disabled")
    verified = await mail_service.verify_access(str(data.email), data.token)
    if verified:
        user_id = await user_service.sign_up(
            data.username, str(data.email), data.password, data.repeat_password
        )
        if not user_id:
            return ResponseMessage(
                message=VerifyResponse(verified=verified), status=200
            )
        await mail_service.remove_access_code(str(data.email))
        # After signup, automatically sign in and return the token
        token = await user_service.sign_in(str(data.email), data.password)
        return ResponseMessage(
            message=TokenResponse(token=token, expires=30 * 24 * 60 * 60), status=200
        )
    return ResponseMessage(message=VerifyResponse(verified=verified), status=200)


@router.subscriber("providers")
async def providers(auth_service: AuthServiceDep) -> ResponseMessage[ProvidersResponse]:
    return ResponseMessage(message=auth_service.get_providers(), status=200)


@router.subscriber("callback")
async def callback(
    data: OAuthConfirmRequest, oauth_service: OAuthServiceDep
) -> ResponseMessage[StatusResponse | TokenResponse]:
    if data.user_id:
        await oauth_service.add_integration(data.user_id, data.provider, data.code)
        return ResponseMessage(message=StatusResponse(), status=200)
    else:
        token = await oauth_service.authorize(data.provider, data.code)
        return ResponseMessage(
            message=TokenResponse(token=token, expires=30 * 24 * 60 * 60), status=200
        )


@router.subscriber("check_username")
async def check(
    data: UsernameRequest, user_service: UserServiceDep
) -> ResponseMessage[BusyResponse]:
    return ResponseMessage(
        message=BusyResponse(
            busy=not await user_service.username_available(data.username)
        ),
        status=200,
    )


@router.subscriber("integrations.get_accounts")
async def get_integration_accounts(
    data: IntegrationAccountsRequest,
    provider_repo: ProviderRepository = Depends(get_provider_repository),
) -> ResponseMessage[dict[str, str]]:
    providers = await provider_repo.get_by_ids(data.integration_ids)
    result = {
        str(p.id): str(p.client_username if p.client_username else p.client_id)
        for p in providers
        if p.client_username or p.client_id
    }
    return ResponseMessage(message=result, status=200)
