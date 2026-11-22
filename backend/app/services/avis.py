from app.core.exceptions import (
    AccesRefuse,
    ConflitMetier,
    RessourceIntrouvable,
)
from app.models.avis import Avis
from app.models.user import User
from app.repositories.avis import AvisRepository
from app.repositories.reservation import ReservationRepository
from app.schemas.avis import AvisCreate


class AvisService:
    def __init__(
        self,
        repository: AvisRepository,
        reservation_repository: ReservationRepository,
    ) -> None:
        self.repository = repository
        self.reservation_repository = reservation_repository

    def create(
        self,
        reservation_id: int,
        payload: AvisCreate,
        current_user: User,
    ) -> Avis:
        reservation = self.reservation_repository.get(reservation_id)
        if reservation is None:
            raise RessourceIntrouvable(
                f"Réservation {reservation_id} introuvable"
            )
        if reservation.borrower_id != current_user.id:
            raise AccesRefuse(
                f"Accès refusé pour la réservation {reservation_id}"
            )
        if reservation.statut != "terminee":
            raise ConflitMetier(
                f"Réservation {reservation_id} non terminée"
            )
        if self.repository.get_by_reservation(reservation_id) is not None:
            raise ConflitMetier(
                "Un avis existe déjà pour cette réservation"
            )
        return self.repository.add(
            Avis(
                reservation_id=reservation_id,
                note=payload.note,
                commentaire=payload.commentaire,
            )
        )
