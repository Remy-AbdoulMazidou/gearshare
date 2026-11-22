from decimal import ROUND_HALF_UP, Decimal

from app.core.exceptions import AccesRefuse, RessourceIntrouvable
from app.models.item import Item
from app.models.user import User
from app.repositories.avis import AvisRepository
from app.repositories.item import ItemRepository
from app.schemas.item import ItemCreate, ItemDetail, ItemRead, ItemUpdate


class ItemService:
    def __init__(
        self,
        repository: ItemRepository,
        avis_repository: AvisRepository,
    ) -> None:
        self.repository = repository
        self.avis_repository = avis_repository

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

    def get_detail(self, item_id: int) -> ItemDetail:
        item = self.get(item_id)
        moyenne, nombre = self.avis_repository.reputation(item.owner_id)
        if nombre == 0 or moyenne is None:
            reputation_moyenne = None
        else:
            arrondie = Decimal(str(moyenne)).quantize(
                Decimal("0.1"),
                rounding=ROUND_HALF_UP,
            )
            reputation_moyenne = float(arrondie)
        return ItemDetail(
            **ItemRead.model_validate(item).model_dump(),
            reputation_moyenne=reputation_moyenne,
            reputation_nombre=nombre,
        )

    def create(self, payload: ItemCreate, current_user: User) -> Item:
        return self.repository.add(
            Item(owner_id=current_user.id, **payload.model_dump())
        )

    def replace(
        self, item_id: int, payload: ItemCreate, current_user: User
    ) -> Item:
        item = self.get(item_id)
        if item.owner_id != current_user.id:
            raise AccesRefuse(f"Accès refusé pour l'item {item_id}")
        for field, value in payload.model_dump().items():
            setattr(item, field, value)
        return item

    def update(
        self, item_id: int, payload: ItemUpdate, current_user: User
    ) -> Item:
        item = self.get(item_id)
        if item.owner_id != current_user.id:
            raise AccesRefuse(f"Accès refusé pour l'item {item_id}")
        values = payload.model_dump(exclude_unset=True)
        for field, value in values.items():
            setattr(item, field, value)
        return item

    def delete(self, item_id: int, current_user: User) -> None:
        item = self.get(item_id)
        if item.owner_id != current_user.id:
            raise AccesRefuse(f"Accès refusé pour l'item {item_id}")
        self.repository.delete(item)
