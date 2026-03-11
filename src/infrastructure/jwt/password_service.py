from passlib.context import CryptContext

from src.domain.services import PasswordService

_crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class BcryptPasswordService(PasswordService):
    def hash_password(self, plain: str) -> str:
        return _crypt_context.hash(plain)

    def verify_password(self, plain: str, hashed: str) -> bool:
        return _crypt_context.verify(plain, hashed)
