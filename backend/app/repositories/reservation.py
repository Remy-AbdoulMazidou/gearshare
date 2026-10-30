from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflitMetier
from app.models.reservation import Reservation


EXCLUDE_CONSTRAINT_NAME = "reservations_active_no_overlap"


class ReservationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, reservation_id: int) -> Reservation | None:
        return self.db.get(Reservation, reservation_id)

    def list(
        self,
        *,
        item_id: int | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Reservation]:
        stmt = select(Reservation)
        if item_id is not None:
            stmt = stmt.where(Reservation.item_id == item_id)
        stmt = stmt.order_by(Reservation.id).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def add(self, reservation: Reservation) -> Reservation:
        try:
            with self.db.begin_nested():
                self.db.add(reservation)
                self.db.flush()
        except IntegrityError as exc:
            if exc.orig.diag.constraint_name == EXCLUDE_CONSTRAINT_NAME:
                raise ConflitMetier(
                    "Le créneau demandé est déjà réservé"
                ) from exc
            raise
        self.db.refresh(reservation)
        return reservation

    def has_active_overlap(
        self,
        item_id: int,
        date_debut: date,
        date_fin: date,
    ) -> bool:
        stmt = select(Reservation.id).where(
            Reservation.item_id == item_id,
            Reservation.statut == "active",
            Reservation.date_debut < date_fin,
            Reservation.date_fin > date_debut,
        )
        return self.db.scalar(stmt) is not None
