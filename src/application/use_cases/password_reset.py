import logging
import random
import string

from src.application.dto import PasswordResetConfirmDTO, PasswordResetRequestDTO
from src.application.ports import EmailProvider, UserRepository, VerificationCodeRepository
from src.domain.exceptions import (
    InvalidPasswordException,
    InvalidVerificationCodeException,
    TooManyAttemptsException,
    UserNotFoundException,
)
from src.domain.services import PasswordService
from src.domain.value_objects import Password

from decouple import config

logger = logging.getLogger(__name__)

CODE_TTL_SECONDS = config("CODE_TTL_SECONDS", cast=int, default=600)
MAX_ATTEMPTS = config("MAX_ATTEMPTS", cast=int, default=5)

class PasswordResetRequestUseCase:
    def __init__(
            self,
            user_repo: UserRepository,
            code_repo: VerificationCodeRepository,
            email_provider: EmailProvider,
                 ) -> None:
        self._user_repo = user_repo
        self._code_repo = code_repo
        self._email_provider = email_provider

    async def execute(self, dto: PasswordResetRequestDTO) -> None:
        user = await self._user_repo.get_by_email(dto.email)
        if user is None:
            return

        code = "".join(random.choices(string.digits, k=6))
        await self._code_repo.save_code(dto.email, code, "password_reset", CODE_TTL_SECONDS)
        await self._email_provider.send_password_reset_code(dto.email, code)

        logger.info(f"Password reset email sent to {user.id} : {dto.email}")

class PasswordResetConfirmUseCase:
    def __init__(
            self,
            user_repo: UserRepository,
            code_repo: VerificationCodeRepository,
            password_service: PasswordService,
    ) -> None:
        self._user_repo = user_repo
        self._code_repo = code_repo
        self._password_service = password_service

    async def execute(self, dto: PasswordResetConfirmDTO) -> None:
        try:
            Password(dto.new_password)
        except ValueError as e:
            raise InvalidPasswordException from e

        user = await self._user_repo.get_by_email(dto.email)
        if user is None:
            raise UserNotFoundException()

        attempts = await self._code_repo.get_attempts(dto.email, "password_reset")
        if attempts >= MAX_ATTEMPTS:
            await self._code_repo.delete_code(dto.email, "password_reset")
            raise TooManyAttemptsException()

        stored_code = await self._code_repo.get_code(dto.email, "password_reset")
        if stored_code != dto.code or stored_code is None:
            await self._code_repo.increment_attempts(dto.email, "password_reset")
            raise InvalidVerificationCodeException()

        await self._code_repo.delete_code(dto.email, "password_reset")

        new_hash = self._password_service.hash_password(dto.new_password)
        user.update_password(new_hash)
        await self._user_repo.update(user)

        logger.info(f"Password reset confirmed to {user.id} : {dto.email}")