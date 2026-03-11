from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import JWTError, jwt

from src.application.ports import JWTProvider
from src.domain.exceptions import InvalidTokenException
from src.infrastructure.config import get_settings

ALGORITHM = "HS256"


class JoseJWTProvider(JWTProvider):
    def __init__(self) -> None:
        self._settings = get_settings()

    def create_access_token(self, user_id: UUID, email: str) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "user_id": str(user_id),
            "email": email,
            "type": "access",
            "iat": now,
            "exp": now + timedelta(minutes=self._settings.jwt_access_ttl_minutes),
        }
        return jwt.encode(payload, self._settings.jwt_secret, algorithm=ALGORITHM)

    def create_refresh_token(self, user_id: UUID) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "user_id": str(user_id),
            "type": "refresh",
            "iat": now,
            "exp": now + timedelta(days=self._settings.jwt_refresh_ttl_days),
        }
        return jwt.encode(payload, self._settings.jwt_secret, algorithm=ALGORITHM)

    def decode_access_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self._settings.jwt_secret, algorithms=[ALGORITHM])
            if payload.get("type") != "access":
                raise InvalidTokenException()
            return payload
        except JWTError as e:
            raise InvalidTokenException() from e

    def decode_refresh_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self._settings.jwt_secret, algorithms=[ALGORITHM])
            if payload.get("type") != "refresh":
                raise InvalidTokenException()
            return payload
        except JWTError as e:
            raise InvalidTokenException() from e
