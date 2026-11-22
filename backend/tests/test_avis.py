from typing import Any

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Avis


def test_ac_02_8_base_refuse_un_second_avis_par_reservation(
    db: Session,
    reservation_active: dict[str, Any],
) -> None:
    db.add(Avis(
        reservation_id=reservation_active["id"],
        note=4,
    ))
    db.flush()

    with pytest.raises(IntegrityError, match="avis_reservation_uq"):
        with db.begin_nested():
            db.add(Avis(
                reservation_id=reservation_active["id"],
                note=5,
            ))
            db.flush()


@pytest.mark.parametrize("note", [0, 6])
def test_ac_02_9_base_refuse_une_note_hors_limites(
    db: Session,
    reservation_active: dict[str, Any],
    note: int,
) -> None:
    with pytest.raises(IntegrityError, match="avis_note_ck"):
        with db.begin_nested():
            db.add(Avis(
                reservation_id=reservation_active["id"],
                note=note,
            ))
            db.flush()


def test_ac_02_10_base_refuse_un_commentaire_trop_long(
    db: Session,
    reservation_active: dict[str, Any],
) -> None:
    with pytest.raises(IntegrityError, match="avis_commentaire_ck"):
        with db.begin_nested():
            db.add(Avis(
                reservation_id=reservation_active["id"],
                note=4,
                commentaire="a" * 501,
            ))
            db.flush()
