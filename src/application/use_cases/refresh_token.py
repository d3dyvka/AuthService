import logging
from uuid import UUID

from src.application.dto import AccessTokenDTO, RefreshTokenDTO
from src.application.ports import JWTProvider, TokenRepository, UserRepository
from src.domain.exceptions import InvalidTokenException, UserNotFoundException

logger = logging.getLogger(__name__)


class RefreshTokenUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        token_repo: TokenRepository,
        jwt_provider: JWTProvider,
    ) -> None:
        self._user_repo = user_repo
        self._token_repo = token_repo
        self._jwt = jwt_provider

    async def execute(self, dto: RefreshTokenDTO) -> AccessTokenDTO:
        try:
            payload = self._jwt.decode_refresh_token(dto.refresh_token)
            user_id = UUID(payload["user_id"])
        except (InvalidTokenException, KeyError, ValueError) as e:
            raise InvalidTokenException() from e

        stored_user_id = await self._token_repo.get_user_id_by_refresh_token(dto.refresh_token)
        if stored_user_id is None or stored_user_id != user_id:
            raise InvalidTokenException()

        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundException()

        await self._token_repo.revoke_refresh_token(dto.refresh_token)

        access_token = self._jwt.create_access_token(user.id, user.email)
        logger.info("Access token refreshed for user (id=%s)", user.id)
        return AccessTokenDTO(access_token=access_token)