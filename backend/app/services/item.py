from app.core.exceptions import RessourceIntrouvable
from app.models.item import Item
from app.models.user import User
from app.repositories.item import ItemRepository
from app.schemas.item import ItemCreate, ItemUpdate


class ItemService:
    def __init__(self, repository: ItemRepository) -> None:
        self.repository = repository

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

    def create(self, payload: ItemCreate, current_user: User) -> Item:
        return self.repository.add(
            Item(owner_id=current_user.id, **payload.model_dump())
        )

    def replace(
        self, item_id: int, payload: ItemCreate, current_user: User
    ) -> Item:
        item = self.get(item_id)
        for field, value in payload.model_dump().items():
            setattr(item, field, value)
        return item

    def update(
        self, item_id: int, payload: ItemUpdate, current_user: User
    ) -> Item:
        item = self.get(item_id)
        values = payload.model_dump(exclude_unset=True)
        for field, value in values.items():
            setattr(item, field, value)
        return item

    def delete(self, item_id: int, current_user: User) -> None:
        item = self.get(item_id)
        self.repository.delete(item)
