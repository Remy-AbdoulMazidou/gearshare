import secrets

from app.core.exceptions import EmailDejaUtilise
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate

DUMMY_PASSWORD_HASH = hash_password(secrets.token_urlsafe())


class AuthService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def register(self, payload: UserCreate) -> User:
        if self.repository.get_by_email(str(payload.email)) is not None:
            raise EmailDejaUtilise("Cette adresse email est déjà utilisée")

        user = User(
            email=str(payload.email),
            password_hash=hash_password(payload.password),
            display_name=payload.display_name,
        )
        return self.repository.add(user)

    def authenticate(self, email: str, password: str) -> User | None:
        user = self.repository.get_by_email(email)
        if user is None:
            verify_password(password, DUMMY_PASSWORD_HASH)
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
