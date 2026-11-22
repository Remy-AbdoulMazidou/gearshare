from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflitMetier
from app.models.avis import Avis
from app.models.item import Item
from app.models.reservation import Reservation

UNIQUE_CONSTRAINT_NAME = "avis_reservation_uq"


class AvisRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_reservation(self, reservation_id: int) -> Avis | None:
        stmt = select(Avis).where(Avis.reservation_id == reservation_id)
        return self.db.scalar(stmt)

    def add(self, avis: Avis) -> Avis:
        try:
            with self.db.begin_nested():
                self.db.add(avis)
                self.db.flush()
        except IntegrityError as exc:
            if exc.orig.diag.constraint_name == UNIQUE_CONSTRAINT_NAME:
                raise ConflitMetier(
                    "Un avis existe déjà pour cette réservation"
                ) from exc
            raise
        self.db.refresh(avis)
        return avis

    def reputation(self, owner_id: int) -> tuple[Decimal | None, int]:
        stmt = (
            select(func.avg(Avis.note), func.count(Avis.id))
            .join(
                Reservation,
                Reservation.id == Avis.reservation_id,
            )
            .join(Item, Item.id == Reservation.item_id)
            .where(
                Item.owner_id == owner_id,
                Reservation.statut == "terminee",
            )
        )
        moyenne, nombre = self.db.execute(stmt).one()
        return moyenne, nombre
