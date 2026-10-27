from app.core.exceptions import RessourceIntrouvable
from app.models.item import Item
from app.repositories.item import ItemRepository
from app.repositories.user import UserRepository
from app.schemas.item import ItemCreate, ItemUpdate


class ItemService:
    def __init__(
        self, repository: ItemRepository, user_repository: UserRepository
    ) -> None:
        self.repository = repository
        self.user_repository = user_repository

    def _verify_owner(self, owner_id: int) -> None:
        if self.user_repository.get(owner_id) is None:
            raise RessourceIntrouvable(f"Utilisateur {owner_id} introuvable")

    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        q: str | None = None,
        disponible: bool | None = None,
    ) -> list[Item]:
        return self.repository.list(
            skip=skip, limit=limit, q=q, disponible=disponible
        )

    def get(self, item_id: int) -> Item:
        item = self.repository.get(item_id)
        if item is None:
            raise RessourceIntrouvable(f"Item {item_id} introuvable")
        return item

    def create(self, payload: ItemCreate) -> Item:
        self._verify_owner(payload.owner_id)
        return self.repository.add(Item(**payload.model_dump()))

    def replace(self, item_id: int, payload: ItemCreate) -> Item:
        item = self.get(item_id)
        self._verify_owner(payload.owner_id)
        for field, value in payload.model_dump().items():
            setattr(item, field, value)
        return item

    def update(self, item_id: int, payload: ItemUpdate) -> Item:
        item = self.get(item_id)
        values = payload.model_dump(exclude_unset=True)
        if "owner_id" in values:
            self._verify_owner(values["owner_id"])
        for field, value in values.items():
            setattr(item, field, value)
        return item

    def delete(self, item_id: int) -> None:
        item = self.get(item_id)
        self.repository.delete(item)
