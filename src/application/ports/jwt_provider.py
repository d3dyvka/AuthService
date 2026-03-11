from abc import ABC, abstractmethod
from uuid import UUID

class JWTProvider(ABC):
    @abstractmethod
    def create_access_token(self, user_id: UUID, email: str) -> str:
        pass

    @abstractmethod
    def create_refresh_token(self, user_id: UUID) -> str:
        pass

    @abstractmethod
    def decode_access_token(self, access_token: str) -> dict:
        pass

    @abstractmethod
    def decode_refresh_token(self, refresh_token: str) -> dict:
        pass
