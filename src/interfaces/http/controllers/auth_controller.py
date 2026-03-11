from fastapi import APIRouter, Depends, status

from src.application.dto import (
    LoginDTO,
    LogoutDTO,
    PasswordResetConfirmDTO,
    PasswordResetRequestDTO,
    RefreshTokenDTO,
    RegisterDTO,
    VerifyLoginDTO,
    VerifyRegistrationDTO,
)
from src.application.use_cases import (
    LoginUseCase,
    LogoutUseCase,
    PasswordResetConfirmUseCase,
    PasswordResetRequestUseCase,
    RefreshTokenUseCase,
    RegisterUseCase,
    ResendVerificationCodeUseCase,
    VerifyLoginUseCase,
    VerifyRegistrationUseCase,
)
from src.interfaces.http.dependencies import (
    get_login_use_case,
    get_logout_use_case,
    get_password_reset_confirm_use_case,
    get_password_reset_request_use_case,
    get_refresh_token_use_case,
    get_register_use_case,
    get_resend_code_use_case,
    get_verify_login_use_case,
    get_verify_registration_use_case,
)
from src.interfaces.http.schemas import (
    AccessTokenResponse,
    ErrorResponse,
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResendCodeRequest,
    TokenPairResponse,
    VerifyCodeRequest,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    responses={
        409: {"model": ErrorResponse, "description": "Email already registered"},
        400: {"model": ErrorResponse, "description": "Invalid password"},
    },
)
async def register(
    body: RegisterRequest,
    use_case: RegisterUseCase = Depends(get_register_use_case),
) -> MessageResponse:
    await use_case.execute(RegisterDTO(email=body.email, password=body.password, name=body.name))
    return MessageResponse(message="verification code sent")


@router.post(
    "/register/verify",
    response_model=TokenPairResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid or expired code"},
        429: {"model": ErrorResponse, "description": "Too many attempts"},
    },
)
async def verify_registration(
    body: VerifyCodeRequest,
    use_case: VerifyRegistrationUseCase = Depends(get_verify_registration_use_case),
) -> TokenPairResponse:
    result = await use_case.execute(VerifyRegistrationDTO(email=body.email, code=body.code))
    return TokenPairResponse(access_token=result.access_token, refresh_token=result.refresh_token)


@router.post(
    "/login",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
        403: {"model": ErrorResponse, "description": "Account not active"},
    },
)
async def login(
    body: LoginRequest,
    use_case: LoginUseCase = Depends(get_login_use_case),
) -> MessageResponse:
    await use_case.execute(LoginDTO(email=body.email, password=body.password))
    return MessageResponse(message="verification code sent")


@router.post(
    "/login/verify",
    response_model=TokenPairResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid or expired code"},
        429: {"model": ErrorResponse, "description": "Too many attempts"},
    },
)
async def verify_login(
    body: VerifyCodeRequest,
    use_case: VerifyLoginUseCase = Depends(get_verify_login_use_case),
) -> TokenPairResponse:
    result = await use_case.execute(VerifyLoginDTO(email=body.email, code=body.code))
    return TokenPairResponse(access_token=result.access_token, refresh_token=result.refresh_token)


@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    status_code=status.HTTP_200_OK,
    responses={401: {"model": ErrorResponse, "description": "Invalid or expired refresh token"}},
)
async def refresh_token(
    body: RefreshTokenRequest,
    use_case: RefreshTokenUseCase = Depends(get_refresh_token_use_case),
) -> AccessTokenResponse:
    result = await use_case.execute(RefreshTokenDTO(refresh_token=body.refresh_token))
    return AccessTokenResponse(access_token=result.access_token)


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
async def logout(
    body: LogoutRequest,
    use_case: LogoutUseCase = Depends(get_logout_use_case),
) -> MessageResponse:
    await use_case.execute(LogoutDTO(refresh_token=body.refresh_token))
    return MessageResponse(message="logged out successfully")


@router.post(
    "/resend-code",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse, "description": "User not found"}},
)
async def resend_code(
    body: ResendCodeRequest,
    use_case: ResendVerificationCodeUseCase = Depends(get_resend_code_use_case),
) -> MessageResponse:
    await use_case.execute(email=body.email, purpose=body.purpose)
    return MessageResponse(message="verification code sent")


@router.post(
    "/password/reset",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
async def password_reset_request(
    body: PasswordResetRequest,
    use_case: PasswordResetRequestUseCase = Depends(get_password_reset_request_use_case),
) -> MessageResponse:
    await use_case.execute(PasswordResetRequestDTO(email=body.email))
    return MessageResponse(message="if the email exists, a reset code has been sent")


@router.post(
    "/password/confirm",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid code or password"},
        429: {"model": ErrorResponse, "description": "Too many attempts"},
    },
)
async def password_reset_confirm(
    body: PasswordResetConfirmRequest,
    use_case: PasswordResetConfirmUseCase = Depends(get_password_reset_confirm_use_case),
) -> MessageResponse:
    await use_case.execute(
        PasswordResetConfirmDTO(
            email=body.email,
            code=body.code,
            new_password=body.new_password,
        )
    )
    return MessageResponse(message="password updated successfully")
