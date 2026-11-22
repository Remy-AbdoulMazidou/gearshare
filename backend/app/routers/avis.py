from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.api.deps import CurrentUser, DbSession
from app.repositories.avis import AvisRepository
from app.repositories.reservation import ReservationRepository
from app.schemas.avis import AvisCreate, AvisRead
from app.schemas.error import ERREUR_401, ERREUR_403, ERREUR_404, ERREUR_409
from app.services.avis import AvisService

router = APIRouter(prefix="/reservations", tags=["avis"])


def get_avis_service(db: DbSession) -> AvisService:
    return AvisService(AvisRepository(db), ReservationRepository(db))


AvisServiceDependency = Annotated[AvisService, Depends(get_avis_service)]


@router.post(
    "/{reservation_id}/avis",
    response_model=AvisRead,
    status_code=201,
    responses={**ERREUR_401, **ERREUR_403, **ERREUR_404, **ERREUR_409},
)
def publier_avis(
    payload: AvisCreate,
    service: AvisServiceDependency,
    current_user: CurrentUser,
    reservation_id: int = Path(ge=1),
):
    return service.create(reservation_id, payload, current_user)
