from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    SmallInteger,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.reservation import Reservation


class Avis(Base):
    __tablename__ = "avis"
    __table_args__ = (
        CheckConstraint("note >= 1 AND note <= 5", name="avis_note_ck"),
        CheckConstraint(
            "commentaire IS NULL OR char_length(commentaire) <= 500",
            name="avis_commentaire_ck",
        ),
        UniqueConstraint("reservation_id", name="avis_reservation_uq"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    reservation_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("reservations.id", ondelete="CASCADE"),
        nullable=False,
    )
    note: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    commentaire: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    reservation: Mapped["Reservation"] = relationship(back_populates="avis")
