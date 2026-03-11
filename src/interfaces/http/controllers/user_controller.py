from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.application.use_cases import GetCurrentUserUseCase
from src.interfaces.http.dependencies import get_current_user_id, get_current_user_use_case
from src.interfaces.http.schemas import ErrorResponse, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses={401: {"model": ErrorResponse, "description": "Unauthorized"}},
)
async def get_me(
    user_id: UUID = Depends(get_current_user_id),
    use_case: GetCurrentUserUseCase = Depends(get_current_user_use_case),
) -> UserResponse:
    result = await use_case.execute(user_id)
    return UserResponse(
        id=result.id,
        email=result.email,
        name=result.name,
        created_at=result.created_at,
    )
