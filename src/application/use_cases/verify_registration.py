import logging

from src.application.dto import TokenPairDTO, VerifyRegistrationDTO
from src.application.ports import JWTProvider, TokenRepository, UserRepository, VerificationCodeRepository
from src.domain.exceptions import (
    InvalidVerificationCodeException,
    TooManyAttemptsException,
    UserNotFoundException,
)

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 5


class VerifyRegistrationUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        code_repo: VerificationCodeRepository,
        token_repo: TokenRepository,
        jwt_provider: JWTProvider,
    ) -> None:
        self._user_repo = user_repo
        self._code_repo = code_repo
        self._token_repo = token_repo
        self._jwt = jwt_provider

    async def execute(self, dto: VerifyRegistrationDTO) -> TokenPairDTO:
        user = await self._user_repo.get_by_email(dto.email)
        if user is None:
            raise UserNotFoundException()

        attempts = await self._code_repo.get_attempts(dto.email, "registration")
        if attempts >= MAX_ATTEMPTS:
            await self._code_repo.delete_code(dto.email, "registration")
            raise TooManyAttemptsException()

        stored_code = await self._code_repo.get_code(dto.email, "registration")
        if stored_code is None or stored_code != dto.code:
            await self._code_repo.increment_attempts(dto.email, "registration")
            raise InvalidVerificationCodeException()

        await self._code_repo.delete_code(dto.email, "registration")

        user.activate()
        await self._user_repo.update(user)

        access_token = self._jwt.create_access_token(user.id, user.email)
        refresh_token = self._jwt.create_refresh_token(user.id)
        await self._token_repo.save_refresh_token(user.id, refresh_token)

        logger.info("User verified registration (id=%s)", user.id)
        return TokenPairDTO(access_token=access_token, refresh_token=refresh_token)
