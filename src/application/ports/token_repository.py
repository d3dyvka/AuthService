from abc import ABC, abstractmethod
from uuid import UUID

class TokenRepository(ABC):
    @abstractmethod
    async def save_refresh_token(self, user_id: UUID, refresh_token: str) -> None:
        pass

    @abstractmethod
    async def get_user_id_by_refresh_token(self, token: str) -> UUID | None:
        pass

    @abstractmethod
    async def revoke_refresh_token(self, token: str) -> None:
        pass

    @abstractmethod
    async def revoke_all_user_tokens(self, user_id: UUID) -> None:
        pass
