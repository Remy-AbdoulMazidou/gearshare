from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Avis
from app.repositories.avis import AvisRepository


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


def creer_reservation_terminee(
    client_bob: TestClient,
    client_alice: TestClient,
    item_velo: dict[str, Any],
) -> dict[str, Any]:
    reservation = client_bob.post("/reservations", json={
        "item_id": item_velo["id"],
        "date_debut": "2026-10-01",
        "date_fin": "2026-10-05",
    }).json()
    response = client_alice.post(
        f"/reservations/{reservation['id']}/cloturer"
    )
    assert response.status_code == 200
    return reservation


def test_ac_02_1_publie_un_avis_entier_sur_reservation_terminee(
    client_bob: TestClient,
    client_alice: TestClient,
    item_velo: dict[str, Any],
) -> None:
    reservation = creer_reservation_terminee(
        client_bob, client_alice, item_velo
    )

    response = client_bob.post(
        f"/reservations/{reservation['id']}/avis",
        json={"note": 4, "commentaire": "Très bon matériel"},
    )

    assert response.status_code == 201
    assert response.json()["reservation_id"] == reservation["id"]
    assert response.json()["note"] == 4


def test_ac_02_2_publie_un_avis_sans_commentaire(
    client_bob: TestClient,
    client_alice: TestClient,
    item_velo: dict[str, Any],
) -> None:
    reservation = creer_reservation_terminee(
        client_bob, client_alice, item_velo
    )

    response = client_bob.post(
        f"/reservations/{reservation['id']}/avis",
        json={"note": 5},
    )

    assert response.status_code == 201
    assert response.json()["note"] == 5


def test_ac_02_3_publie_un_commentaire_de_500_caracteres(
    client_bob: TestClient,
    client_alice: TestClient,
    item_velo: dict[str, Any],
) -> None:
    reservation = creer_reservation_terminee(
        client_bob, client_alice, item_velo
    )

    response = client_bob.post(
        f"/reservations/{reservation['id']}/avis",
        json={"note": 3, "commentaire": "a" * 500},
    )

    assert response.status_code == 201


def test_ac_02_4_publie_sans_authentification_renvoie_401(
    raw_client: TestClient,
    reservation_active: dict[str, Any],
) -> None:
    response = raw_client.post(
        f"/reservations/{reservation_active['id']}/avis",
        json={"note": 4},
    )

    assert response.status_code == 401


def test_ac_02_5_publie_pour_reservation_inexistante_renvoie_404(
    client_bob: TestClient,
) -> None:
    response = client_bob.post(
        "/reservations/999/avis",
        json={"note": 4},
    )

    assert response.status_code == 404


def test_ac_02_6_publie_sur_reservation_d_un_autre_emprunteur_renvoie_403(
    client_bob: TestClient,
    client_alice: TestClient,
    item_velo: dict[str, Any],
) -> None:
    reservation = creer_reservation_terminee(
        client_bob, client_alice, item_velo
    )

    response = client_alice.post(
        f"/reservations/{reservation['id']}/avis",
        json={"note": 4},
    )

    assert response.status_code == 403


@pytest.mark.parametrize("statut", ["active", "annulee"])
def test_ac_02_7_publie_sur_reservation_active_ou_annulee_renvoie_409(
    statut: str,
    client_bob: TestClient,
    item_velo: dict[str, Any],
) -> None:
    reservation = client_bob.post("/reservations", json={
        "item_id": item_velo["id"],
        "date_debut": "2026-10-01",
        "date_fin": "2026-10-05",
    }).json()
    if statut == "annulee":
        response = client_bob.post(
            f"/reservations/{reservation['id']}/annuler"
        )
        assert response.status_code == 200

    response = client_bob.post(
        f"/reservations/{reservation['id']}/avis",
        json={"note": 4},
    )

    assert response.status_code == 409


def test_ac_02_8_publie_un_second_avis_renvoie_409(
    client_bob: TestClient,
    client_alice: TestClient,
    item_velo: dict[str, Any],
) -> None:
    reservation = creer_reservation_terminee(
        client_bob, client_alice, item_velo
    )
    first_response = client_bob.post(
        f"/reservations/{reservation['id']}/avis",
        json={"note": 4},
    )
    assert first_response.status_code == 201

    second_response = client_bob.post(
        f"/reservations/{reservation['id']}/avis",
        json={"note": 5},
    )

    assert second_response.status_code == 409


def test_ac_02_8_course_simulee_renvoie_409(
    db: Session,
    client_bob: TestClient,
    client_alice: TestClient,
    item_velo: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    reservation = creer_reservation_terminee(
        client_bob, client_alice, item_velo
    )
    first_response = client_bob.post(
        f"/reservations/{reservation['id']}/avis",
        json={"note": 4},
    )
    assert first_response.status_code == 201

    monkeypatch.setattr(
        AvisRepository,
        "get_by_reservation",
        lambda self, reservation_id: None,
    )

    response = client_bob.post(
        f"/reservations/{reservation['id']}/avis",
        json={"note": 5},
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Un avis existe déjà pour cette réservation"
    }
    avis_count = (
        db.query(Avis)
        .filter(Avis.reservation_id == reservation["id"])
        .count()
    )
    assert avis_count == 1


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"note": 4.5},
        {"note": "4"},
        {"note": 0},
        {"note": 6},
    ],
)
def test_ac_02_9_valide_une_note_obligatoire_entiere_et_entre_1_et_5(
    payload: dict[str, Any],
    client_bob: TestClient,
    client_alice: TestClient,
    item_velo: dict[str, Any],
) -> None:
    reservation = creer_reservation_terminee(
        client_bob, client_alice, item_velo
    )

    response = client_bob.post(
        f"/reservations/{reservation['id']}/avis",
        json=payload,
    )

    assert response.status_code == 422


def test_ac_02_10_refuse_un_commentaire_superieur_a_500_caracteres(
    client_bob: TestClient,
    client_alice: TestClient,
    item_velo: dict[str, Any],
) -> None:
    reservation = creer_reservation_terminee(
        client_bob, client_alice, item_velo
    )

    response = client_bob.post(
        f"/reservations/{reservation['id']}/avis",
        json={"note": 4, "commentaire": "a" * 501},
    )

    assert response.status_code == 422
