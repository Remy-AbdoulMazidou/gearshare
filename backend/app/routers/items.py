from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response

from app.api.deps import CurrentUser, DbSession
from app.repositories.item import ItemRepository
from app.schemas.item import ItemCreate, ItemRead, ItemUpdate
from app.services.item import ItemService

router = APIRouter(prefix="/items", tags=["items"])


def get_item_service(db: DbSession) -> ItemService:
    return ItemService(ItemRepository(db))


ItemServiceDependency = Annotated[ItemService, Depends(get_item_service)]


@router.get("", response_model=list[ItemRead])
def list_items(
    service: ItemServiceDependency,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    q: str | None = None,
    disponible: bool | None = None,
):
    return service.list(
        skip=skip, limit=limit, q=q, disponible=disponible
    )


@router.post("", response_model=ItemRead, status_code=201)
def create_item(
    payload: ItemCreate, service: ItemServiceDependency, current_user: CurrentUser
):
    return service.create(payload, current_user)


@router.get("/{item_id}", response_model=ItemRead)
def get_item(
    service: ItemServiceDependency, item_id: int = Path(ge=1)
):
    return service.get(item_id)


@router.put("/{item_id}", response_model=ItemRead)
def replace_item(
    payload: ItemCreate,
    service: ItemServiceDependency,
    current_user: CurrentUser,
    item_id: int = Path(ge=1),
):
    return service.replace(item_id, payload, current_user)


@router.patch("/{item_id}", response_model=ItemRead)
def update_item(
    payload: ItemUpdate,
    service: ItemServiceDependency,
    current_user: CurrentUser,
    item_id: int = Path(ge=1),
):
    return service.update(item_id, payload, current_user)


@router.delete("/{item_id}", status_code=204, response_class=Response)
def delete_item(
    service: ItemServiceDependency,
    current_user: CurrentUser,
    item_id: int = Path(ge=1),
):
    service.delete(item_id, current_user)
