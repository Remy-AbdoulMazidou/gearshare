from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from app.api.deps import CurrentUser, DbSession
from app.repositories.item import ItemRepository
from app.repositories.reservation import ReservationRepository
from app.schemas.reservation import ReservationCreate, ReservationRead, ReservationUpdate
from app.services.reservation import ReservationService

router = APIRouter(prefix="/reservations", tags=["reservations"])


def get_reservation_service(db: DbSession) -> ReservationService:
    return ReservationService(
        ReservationRepository(db), ItemRepository(db)
    )


ReservationServiceDependency = Annotated[
    ReservationService, Depends(get_reservation_service)
]


@router.get("", response_model=list[ReservationRead])
def list_reservations(
    service: ReservationServiceDependency,
    current_user: CurrentUser,
    item_id: int | None = Query(default=None, ge=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    return service.list(item_id=item_id, skip=skip, limit=limit)


@router.post("", response_model=ReservationRead, status_code=201)
def create_reservation(
    payload: ReservationCreate,
    service: ReservationServiceDependency,
    current_user: CurrentUser,
):
    return service.create(payload, current_user)


@router.get("/{reservation_id}", response_model=ReservationRead)
def get_reservation(
    service: ReservationServiceDependency,
    current_user: CurrentUser,
    reservation_id: int = Path(ge=1),
):
    return service.get(reservation_id)


@router.patch("/{reservation_id}", response_model=ReservationRead)
def update_reservation(
    payload: ReservationUpdate,
    service: ReservationServiceDependency,
    current_user: CurrentUser,
    reservation_id: int = Path(ge=1),
):
    return service.cancel(reservation_id)


@router.post("/{reservation_id}/annuler", response_model=ReservationRead)
def annuler_reservation(
    service: ReservationServiceDependency,
    current_user: CurrentUser,
    reservation_id: int = Path(ge=1),
):
    return service.cancel(reservation_id)
