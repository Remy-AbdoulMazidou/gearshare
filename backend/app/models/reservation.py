from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    ForeignKey,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import ExcludeConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.item import Item
    from app.models.user import User


class Reservation(Base):
    __tablename__ = "reservations"
    __table_args__ = (
        CheckConstraint("date_fin > date_debut", name="dates_coherentes"),
        CheckConstraint(
            "statut IN ('active', 'annulee', 'terminee')", name="statut_valide"
        ),
        ExcludeConstraint(
            ("item_id", "="),
            (text("daterange(date_debut, date_fin, '[)')"), "&&"),
            using="gist",
            where=text("statut = 'active'"),
            name="reservations_active_no_overlap",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    item_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    borrower_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False, index=True
    )
    date_debut: Mapped[date] = mapped_column(Date, nullable=False)
    date_fin: Mapped[date] = mapped_column(Date, nullable=False)
    statut: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'active'")
    )

    item: Mapped["Item"] = relationship(back_populates="reservations")
    borrower: Mapped["User"] = relationship(back_populates="reservations")
