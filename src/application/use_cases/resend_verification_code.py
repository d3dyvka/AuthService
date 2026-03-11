import logging
import random
import string

from src.application.ports import EmailProvider, UserRepository, VerificationCodeRepository
from src.domain.exceptions import UserNotFoundException

logger = logging.getLogger(__name__)

CODE_TTL_SECONDS = 600


class ResendVerificationCodeUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        code_repo: VerificationCodeRepository,
        email_provider: EmailProvider,
    ) -> None:
        self._user_repo = user_repo
        self._code_repo = code_repo
        self._email_provider = email_provider

    async def execute(self, email: str, purpose: str) -> None:
        user = await self._user_repo.get_by_email(email)
        if user is None:
            raise UserNotFoundException()

        await self._code_repo.delete_code(email, purpose)

        code = "".join(random.choices(string.digits, k=6))
        await self._code_repo.save_code(email, code, purpose, CODE_TTL_SECONDS)
        await self._email_provider.send_verification_code(email, code, purpose)

        logger.info("Verification code resent for purpose=%s user_id=%s", purpose, user.id)
