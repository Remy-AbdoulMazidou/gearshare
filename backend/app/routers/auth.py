from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import DbSession
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserRead
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(db: DbSession) -> AuthService:
    return AuthService(UserRepository(db))


AuthServiceDependency = Annotated[AuthService, Depends(get_auth_service)]


@router.post("/register", response_model=UserRead, status_code=201)
def register(payload: UserCreate, service: AuthServiceDependency):
    return service.register(payload)
