import logging
import random
import string

from src.application.dto import RegisterDTO
from src.application.ports import EmailProvider, UserRepository, VerificationCodeRepository
from src.domain.entities import User
from src.domain.exceptions import InvalidPasswordException, UserAlreadyExistsException
from src.domain.services import PasswordService
from src.domain.value_objects import Password

logger = logging.getLogger(__name__)

CODE_TTL_SECONDS = 600


class RegisterUseCase:
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

    async def execute(self, dto: RegisterDTO) -> None:
        try:
            Password(dto.password)
        except ValueError as e:
            raise InvalidPasswordException() from e

        existing = await self._user_repo.get_by_email(dto.email)
        if existing is not None:
            raise UserAlreadyExistsException()

        password_hash = self._password_service.hash_password(dto.password)
        user = User(email=dto.email, password_hash=password_hash, name=dto.name)
        await self._user_repo.save(user)

        code = "".join(random.choices(string.digits, k=6))
        await self._code_repo.save_code(dto.email, code, "registration", CODE_TTL_SECONDS)
        await self._email_provider.send_verification_code(dto.email, code, "registration")

        logger.info("Registration started for user (id=%s)", user.id)
