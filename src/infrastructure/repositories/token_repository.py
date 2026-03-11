from datetime import datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports import TokenRepository
from src.infrastructure.config import get_settings
from src.infrastructure.database.models import RefreshTokenModel

settings = get_settings()


class SQLAlchemyTokenRepository(TokenRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save_refresh_token(self, user_id: UUID, token: str) -> None:
        expires_at = datetime.utcnow() + timedelta(days=settings.jwt_refresh_ttl_days)
        model = RefreshTokenModel(
            id=uuid4(),
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            is_revoked=False,
        )
        self._session.add(model)
        await self._session.flush()

    async def get_user_id_by_refresh_token(self, token: str) -> UUID | None:
        now = datetime.utcnow()
        result = await self._session.execute(
            select(RefreshTokenModel).where(
                RefreshTokenModel.token == token,
                RefreshTokenModel.is_revoked.is_(False),
                RefreshTokenModel.expires_at > now,
            )
        )
        model = result.scalar_one_or_none()
        return model.user_id if model else None

    async def revoke_refresh_token(self, token: str) -> None:
        await self._session.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.token == token)
            .values(is_revoked=True)
        )
        await self._session.flush()

    async def revoke_all_user_tokens(self, user_id: UUID) -> None:
        await self._session.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user_id)
            .values(is_revoked=True)
        )
        await self._session.flush()
