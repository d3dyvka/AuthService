from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.dto import LoginDTO, RegisterDTO, VerifyRegistrationDTO
from src.application.use_cases import LoginUseCase, RegisterUseCase, VerifyRegistrationUseCase
from src.domain.entities import User
from src.domain.exceptions import (
    InvalidCredentialsException,
    InvalidPasswordException,
    InvalidVerificationCodeException,
    TooManyAttemptsException,
    UserAlreadyExistsException,
)


def make_user(**kwargs) -> User:
    defaults = dict(email="test@example.com", password_hash="hashed", name="Test")
    defaults.update(kwargs)
    return User(**defaults)


# ---- RegisterUseCase ----

class TestRegisterUseCase:
    def setup_method(self):
        self.user_repo = AsyncMock()
        self.code_repo = AsyncMock()
        self.email_provider = AsyncMock()
        self.password_service = MagicMock()
        self.password_service.hash_password.return_value = "hashed_pw"
        self.use_case = RegisterUseCase(
            self.user_repo, self.code_repo, self.email_provider, self.password_service
        )

    async def test_success(self):
        self.user_repo.get_by_email.return_value = None
        self.user_repo.save.return_value = make_user()
        await self.use_case.execute(RegisterDTO("new@example.com", "Password123", "Test"))
        self.user_repo.save.assert_called_once()
        self.code_repo.save_code.assert_called_once()
        self.email_provider.send_verification_code.assert_called_once()

    async def test_duplicate_email(self):
        self.user_repo.get_by_email.return_value = make_user()
        with pytest.raises(UserAlreadyExistsException):
            await self.use_case.execute(RegisterDTO("existing@example.com", "Password123", "Test"))

    async def test_invalid_password(self):
        self.user_repo.get_by_email.return_value = None
        with pytest.raises(InvalidPasswordException):
            await self.use_case.execute(RegisterDTO("new@example.com", "short", "Test"))


# ---- LoginUseCase ----

class TestLoginUseCase:
    def setup_method(self):
        self.user_repo = AsyncMock()
        self.code_repo = AsyncMock()
        self.email_provider = AsyncMock()
        self.password_service = MagicMock()
        self.use_case = LoginUseCase(
            self.user_repo, self.code_repo, self.email_provider, self.password_service
        )

    async def test_success(self):
        user = make_user(is_active=True)
        self.user_repo.get_by_email.return_value = user
        self.password_service.verify_password.return_value = True
        await self.use_case.execute(LoginDTO("test@example.com", "Password123"))
        self.code_repo.save_code.assert_called_once()

    async def test_user_not_found(self):
        self.user_repo.get_by_email.return_value = None
        with pytest.raises(InvalidCredentialsException):
            await self.use_case.execute(LoginDTO("no@example.com", "Password123"))

    async def test_wrong_password(self):
        user = make_user(is_active=True)
        self.user_repo.get_by_email.return_value = user
        self.password_service.verify_password.return_value = False
        with pytest.raises(InvalidCredentialsException):
            await self.use_case.execute(LoginDTO("test@example.com", "WrongPass1"))


# ---- VerifyRegistrationUseCase ----

class TestVerifyRegistrationUseCase:
    def setup_method(self):
        self.user_repo = AsyncMock()
        self.code_repo = AsyncMock()
        self.token_repo = AsyncMock()
        self.jwt = MagicMock()
        self.jwt.create_access_token.return_value = "access_token"
        self.jwt.create_refresh_token.return_value = "refresh_token"
        self.use_case = VerifyRegistrationUseCase(
            self.user_repo, self.code_repo, self.token_repo, self.jwt
        )

    async def test_success(self):
        user = make_user()
        self.user_repo.get_by_email.return_value = user
        self.code_repo.get_attempts.return_value = 0
        self.code_repo.get_code.return_value = "123456"
        self.user_repo.update.return_value = user
        result = await self.use_case.execute(VerifyRegistrationDTO("test@example.com", "123456"))
        assert result.access_token == "access_token"
        assert result.refresh_token == "refresh_token"

    async def test_wrong_code(self):
        user = make_user()
        self.user_repo.get_by_email.return_value = user
        self.code_repo.get_attempts.return_value = 0
        self.code_repo.get_code.return_value = "111111"
        with pytest.raises(InvalidVerificationCodeException):
            await self.use_case.execute(VerifyRegistrationDTO("test@example.com", "999999"))

    async def test_too_many_attempts(self):
        user = make_user()
        self.user_repo.get_by_email.return_value = user
        self.code_repo.get_attempts.return_value = 5
        with pytest.raises(TooManyAttemptsException):
            await self.use_case.execute(VerifyRegistrationDTO("test@example.com", "123456"))
