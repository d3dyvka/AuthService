import logging

from src.application.dto import LogoutDTO
from src.application.ports import TokenRepository

logger = logging.getLogger(__name__)


class LogoutUseCase:
    def __init__(self, token_repo: TokenRepository) -> None:
        self._token_repo = token_repo

    async def execute(self, dto: LogoutDTO) -> None:
        await self._token_repo.revoke_refresh_token(dto.refresh_token)
        logger.info("User logged out (token revoked)")
