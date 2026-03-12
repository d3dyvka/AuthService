from datetime import datetime
from uuid import UUID

import pytest

from src.domain.entities import User
from src.domain.value_objects import Password


class TestUserEntity:
    def test_default_values(self):
        user = User(email="test@example.com", password_hash="hashed", name="Test")
        assert isinstance(user.id, UUID)
        assert user.is_active is False
        assert user.is_email_verified is False
        assert user.last_login_at is None
        assert isinstance(user.created_at, datetime)

    def test_activate(self):
        user = User(email="test@example.com", password_hash="hashed", name="Test")
        before = user.updated_at
        user.activate()
        assert user.is_active is True
        assert user.is_email_verified is True
        assert user.updated_at >= before

    def test_update_last_login(self):
        user = User(email="test@example.com", password_hash="hashed", name="Test")
        assert user.last_login_at is None
        user.update_last_login()
        assert user.last_login_at is not None
        assert isinstance(user.last_login_at, datetime)

    def test_update_password(self):
        user = User(email="test@example.com", password_hash="old_hash", name="Test")
        user.update_password("new_hash")
        assert user.password_hash == "new_hash"


class TestPasswordValueObject:
    def test_valid_password(self):
        pwd = Password("Password123")
        assert str(pwd) == "Password123"

    def test_too_short(self):
        with pytest.raises(ValueError, match="at least 8 characters"):
            Password("Pass1")

    def test_no_digit(self):
        with pytest.raises(ValueError, match="at least one digit"):
            Password("PasswordOnly")

    def test_no_letter(self):
        with pytest.raises(ValueError, match="at least one letter"):
            Password("12345678")

    def test_frozen(self):
        pwd = Password("Password123")
        with pytest.raises(Exception):
            pwd.value = "other"  # type: ignore[misc]
