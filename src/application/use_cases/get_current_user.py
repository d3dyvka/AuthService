from uuid import UUID

from src.application.dto import UserDTO
from src.application.ports import UserRepository
from src.domain.exceptions import UserNotFoundException

class GetCurrentUserUseCase:
    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, user_id: UUID) -> UserDTO:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        return UserDTO(id=user.id, email=user.email, name=user.name, created_at=user.created_at)
