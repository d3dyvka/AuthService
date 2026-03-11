from abc import ABC, abstractmethod

from src.domain.entities import User


class VerificationCodeRepository(ABC):
    @abstractmethod
    async def save_code(self, email: str, code: str, purpose: str, ttl_seconds: int) -> None:
        pass

    @abstractmethod
    async def get_code(self, email: str, purpose: str) -> None:
        pass

    @abstractmethod
    async def delete_code(self, email: str, purpose: str) -> None:
        pass

    @abstractmethod
    async def increment_attempts(self, email: str, purpose: str) -> int:
        pass

    @abstractmethod
    async def get_attempts(self, email: str, purpose: str) -> int:
        pass