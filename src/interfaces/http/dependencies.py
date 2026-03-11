from collections.abc import AsyncGenerator
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.application.ports import (
    EmailProvider,
    JWTProvider,
    TokenRepository,
    UserRepository,
    VerificationCodeRepository,
)
from src.application.use_cases import (
    GetCurrentUserUseCase,
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
from src.domain.exceptions import InvalidTokenException
from src.infrastructure.cashe import RedisVerificationCodeRepository, get_redis_client
from src.infrastructure.database import get_session
from src.infrastructure.email import SMTPEmailProvider
from src.infrastructure.jwt import BcryptPasswordService, JoseJWTProvider
from src.infrastructure.repositories import SQLAlchemyTokenRepository, SQLAlchemyUserRepository

async def get_db():
    async for session in get_session():
        yield session


async def get_user_repository(session=Depends(get_db)) -> UserRepository:
    return SQLAlchemyUserRepository(session)


async def get_token_repository(session=Depends(get_db)) -> TokenRepository:
    return SQLAlchemyTokenRepository(session)


async def get_verification_code_repository() -> VerificationCodeRepository:
    return RedisVerificationCodeRepository(get_redis_client())


async def get_email_provider() -> EmailProvider:
    return SMTPEmailProvider()


async def get_password_service() -> BcryptPasswordService:
    return BcryptPasswordService()


async def get_jwt_provider() -> JWTProvider:
    return JoseJWTProvider()


async def get_register_use_case(
    user_repo: UserRepository = Depends(get_user_repository),
    code_repo: VerificationCodeRepository = Depends(get_verification_code_repository),
    email_provider: EmailProvider = Depends(get_email_provider),
    password_service: BcryptPasswordService = Depends(get_password_service),
) -> RegisterUseCase:
    return RegisterUseCase(user_repo, code_repo, email_provider, password_service)


async def get_verify_registration_use_case(
    user_repo: UserRepository = Depends(get_user_repository),
    code_repo: VerificationCodeRepository = Depends(get_verification_code_repository),
    token_repo: TokenRepository = Depends(get_token_repository),
    jwt_provider: JWTProvider = Depends(get_jwt_provider),
) -> VerifyRegistrationUseCase:
    return VerifyRegistrationUseCase(user_repo, code_repo, token_repo, jwt_provider)


async def get_login_use_case(
    user_repo: UserRepository = Depends(get_user_repository),
    code_repo: VerificationCodeRepository = Depends(get_verification_code_repository),
    email_provider: EmailProvider = Depends(get_email_provider),
    password_service: BcryptPasswordService = Depends(get_password_service),
) -> LoginUseCase:
    return LoginUseCase(user_repo, code_repo, email_provider, password_service)


async def get_verify_login_use_case(
    user_repo: UserRepository = Depends(get_user_repository),
    code_repo: VerificationCodeRepository = Depends(get_verification_code_repository),
    token_repo: TokenRepository = Depends(get_token_repository),
    jwt_provider: JWTProvider = Depends(get_jwt_provider),
) -> VerifyLoginUseCase:
    return VerifyLoginUseCase(user_repo, code_repo, token_repo, jwt_provider)


async def get_refresh_token_use_case(
    user_repo: UserRepository = Depends(get_user_repository),
    token_repo: TokenRepository = Depends(get_token_repository),
    jwt_provider: JWTProvider = Depends(get_jwt_provider),
) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(user_repo, token_repo, jwt_provider)


async def get_logout_use_case(
    token_repo: TokenRepository = Depends(get_token_repository),
) -> LogoutUseCase:
    return LogoutUseCase(token_repo)


async def get_current_user_use_case(
    user_repo: UserRepository = Depends(get_user_repository),
) -> GetCurrentUserUseCase:
    return GetCurrentUserUseCase(user_repo)


async def get_resend_code_use_case(
    user_repo: UserRepository = Depends(get_user_repository),
    code_repo: VerificationCodeRepository = Depends(get_verification_code_repository),
    email_provider: EmailProvider = Depends(get_email_provider),
) -> ResendVerificationCodeUseCase:
    return ResendVerificationCodeUseCase(user_repo, code_repo, email_provider)


async def get_password_reset_request_use_case(
    user_repo: UserRepository = Depends(get_user_repository),
    code_repo: VerificationCodeRepository = Depends(get_verification_code_repository),
    email_provider: EmailProvider = Depends(get_email_provider),
) -> PasswordResetRequestUseCase:
    return PasswordResetRequestUseCase(user_repo, code_repo, email_provider)


async def get_password_reset_confirm_use_case(
    user_repo: UserRepository = Depends(get_user_repository),
    code_repo: VerificationCodeRepository = Depends(get_verification_code_repository),
    password_service: BcryptPasswordService = Depends(get_password_service),
) -> PasswordResetConfirmUseCase:
    return PasswordResetConfirmUseCase(user_repo, code_repo, password_service)

_http_bearer = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(_http_bearer),
    jwt_provider: JWTProvider = Depends(get_jwt_provider),
) -> UUID:
    try:
        payload = jwt_provider.decode_access_token(credentials.credentials)
        return UUID(payload["user_id"])
    except (InvalidTokenException, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "invalid_token", "message": "Invalid or expired token"},
            headers={"WWW-Authenticate": "Bearer"},
        )
