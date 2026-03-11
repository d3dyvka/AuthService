import logging
import random
import string

from src.application.dto import LoginDTO
from src.application.ports import EmailProvider, UserRepository, VerificationCodeRepository
from src.domain.exceptions import InvalidCredentialsException, UserNotActiveException
from src.domain.services import PasswordService

from decouple import config

logger = logging.getLogger(__name__)

CODE_TTL_SECONDS = config("CODE_TTL_SECONDS")

class LoginUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        code_repo: VerificationCodeRepository,
        email_provider: EmailProvider,
        password_service: PasswordService,
    ) -> None:
        self._user_repo = user_repo
        self._code_repo = code_repo
        self._email_provider = email_provider
        self._password_service = password_service

    async def execute(self, dto: LoginDTO) -> None:
        user = await self._user_repo.get_by_email(dto.email)
        if user is None:
            raise InvalidCredentialsException()

        if not self._password_service.verify_password(dto.password, user.password_hash):
            raise InvalidCredentialsException()

        if not user.is_active:
            raise UserNotActiveException()

        code = "".join(random.choices(string.digits, k=6))
        await self._code_repo.save_code(dto.email, code, "login", CODE_TTL_SECONDS)
        await self._email_provider.send_verification_code(dto.email, code, "login")

        logger.info("Login initiated for user (id=%s)", user.id)
