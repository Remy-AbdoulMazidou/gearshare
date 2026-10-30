import logging

from app.core.exceptions import ConflitMetier, RessourceIntrouvable
from app.models.reservation import Reservation
from app.repositories.item import ItemRepository
from app.repositories.reservation import ReservationRepository
from app.repositories.user import UserRepository
from app.schemas.reservation import ReservationCreate

logger = logging.getLogger(__name__)


def envoyer_notification_annulation(reservation_id: int) -> None:
    logger.info("Notification d'annulation envoyée pour la réservation %s", reservation_id)


class ReservationService:
    def __init__(
        self,
        repository: ReservationRepository,
        item_repository: ItemRepository,
        user_repository: UserRepository,
    ) -> None:
        self.repository = repository
        self.item_repository = item_repository
        self.user_repository = user_repository

    def list(
        self,
        *,
        item_id: int | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Reservation]:
        return self.repository.list(item_id=item_id, skip=skip, limit=limit)

    def get(self, reservation_id: int) -> Reservation:
        reservation = self.repository.get(reservation_id)
        if reservation is None:
            raise RessourceIntrouvable(
                f"Réservation {reservation_id} introuvable"
            )
        return reservation

    def create(self, payload: ReservationCreate) -> Reservation:
        item = self.item_repository.get(payload.item_id)
        if item is None:
            raise RessourceIntrouvable(f"Item {payload.item_id} introuvable")
        if not item.disponible:
            raise ConflitMetier(f"Item {payload.item_id} indisponible")
        if self.user_repository.get(payload.borrower_id) is None:
            raise RessourceIntrouvable(
                f"Utilisateur {payload.borrower_id} introuvable"
            )
        if self.repository.has_active_overlap(
            payload.item_id, payload.date_debut, payload.date_fin
        ):
            raise ConflitMetier("Le créneau demandé est déjà réservé")
        return self.repository.add(Reservation(**payload.model_dump()))

    def cancel(self, reservation_id: int) -> Reservation:
        reservation = self.get(reservation_id)
        if reservation.statut != "active":
            raise ConflitMetier(
                f"Réservation {reservation_id} non active"
            )
        reservation.statut = "annulee"
        try:
            envoyer_notification_annulation(reservation_id=reservation_id)
        except (ConnectionError, TimeoutError):
            logger.warning(
                "Notification d'annulation non envoyée pour la réservation %s",
                reservation_id,
            )
        return reservation
