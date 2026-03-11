import redis.asyncio as aioredis

from src.application.ports import VerificationCodeRepository


class RedisVerificationCodeRepository(VerificationCodeRepository):
    def __init__(self, redis: aioredis.Redis) -> None:
        self._redis = redis

    def _code_key(self, email: str, purpose: str) -> str:
        return f"verification_code:{purpose}:{email}"

    def _attempts_key(self, email: str, purpose: str) -> str:
        return f"verification_attempts:{purpose}:{email}"

    async def save_code(self, email: str, code: str, purpose: str, ttl_seconds: int) -> None:
        await self._redis.set(self._code_key(email, purpose), code, ex=ttl_seconds)
        await self._redis.delete(self._attempts_key(email, purpose))

    async def get_code(self, email: str, purpose: str) -> str | None:
        value = await self._redis.get(self._code_key(email, purpose))
        return value  # already decoded because decode_responses=True

    async def delete_code(self, email: str, purpose: str) -> None:
        await self._redis.delete(self._code_key(email, purpose))
        await self._redis.delete(self._attempts_key(email, purpose))

    async def increment_attempts(self, email: str, purpose: str) -> int:
        key = self._attempts_key(email, purpose)
        count = await self._redis.incr(key)
        await self._redis.expire(key, 600)
        return count

    async def get_attempts(self, email: str, purpose: str) -> int:
        value = await self._redis.get(self._attempts_key(email, purpose))
        return int(value) if value is not None else 0
