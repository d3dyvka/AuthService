from abc import ABC, abstractmethod

class EmailProvider(ABC):
    @abstractmethod
    async def send_verification_code(self, to_email: str, verification_code: str, purpose: str) -> None:
        pass
    @abstractmethod
    async def send_password_reset_code(self, to_email: str, code: str) -> None:
        pass