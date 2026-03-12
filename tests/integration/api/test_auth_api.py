from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from src.application.dto import TokenPairDTO
from src.interfaces.http.dependencies import (
    get_register_use_case,
    get_verify_registration_use_case,
)
from src.main import app


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


class TestRegisterEndpoint:
    async def test_register_success(self, client):
        mock_uc = AsyncMock()
        mock_uc.execute.return_value = None
        app.dependency_overrides[get_register_use_case] = lambda: mock_uc

        response = await client.post(
            "/auth/register",
            json={"email": "user@example.com", "password": "Password123", "name": "John"},
        )
        assert response.status_code == 200
        assert response.json()["message"] == "verification code sent"
        app.dependency_overrides.clear()

    async def test_register_invalid_email(self, client):
        response = await client.post(
            "/auth/register",
            json={"email": "not-an-email", "password": "Password123", "name": "John"},
        )
        assert response.status_code == 422

    async def test_register_short_password(self, client):
        response = await client.post(
            "/auth/register",
            json={"email": "user@example.com", "password": "short", "name": "John"},
        )
        assert response.status_code == 422


class TestVerifyRegistrationEndpoint:
    async def test_verify_success(self, client):
        mock_uc = AsyncMock()
        mock_uc.execute.return_value = TokenPairDTO(
            access_token="access123", refresh_token="refresh456"
        )
        app.dependency_overrides[get_verify_registration_use_case] = lambda: mock_uc

        response = await client.post(
            "/auth/register/verify",
            json={"email": "user@example.com", "code": "123456"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "access123"
        assert data["refresh_token"] == "refresh456"
        app.dependency_overrides.clear()

    async def test_verify_invalid_code_format(self, client):
        response = await client.post(
            "/auth/register/verify",
            json={"email": "user@example.com", "code": "abc"},
        )
        assert response.status_code == 422


class TestHealthEndpoint:
    async def test_health(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}