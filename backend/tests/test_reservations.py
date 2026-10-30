from datetime import date
from typing import Any
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflitMetier, RessourceIntrouvable
from app.models import Item, Reservation, User
from app.repositories.item import ItemRepository
from app.repositories.reservation import ReservationRepository
from app.schemas.reservation import ReservationCreate
from app.services.reservation import ReservationService

from app.services import reservation as reservation_service


# Cas nominaux


def test_creer_reservation_renvoie_201_avec_statut_active(
    client: TestClient, item_velo: dict[str, Any], alice: User
) -> None:
    response = client.post("/reservations", json={
        "item_id": item_velo["id"],
        "date_debut": "2026-10-01", "date_fin": "2026-10-05",
    })

    assert response.status_code == 201
    corps = response.json()
    assert corps["id"] == 1
    assert corps["item_id"] == item_velo["id"]
    assert corps["borrower_id"] == alice.id
    assert corps["statut"] == "active"


@pytest.mark.parametrize(
    ("client_fixture", "status_code"),
    [("raw_client", 401), ("client_alice", 201), ("client_bob", 201)],
)
def test_matrice_creation_reservation(
    request: pytest.FixtureRequest,
    client_fixture: str,
    status_code: int,
    item_velo: dict[str, Any],
) -> None:
    test_client = request.getfixturevalue(client_fixture)
    response = test_client.post("/reservations", json={
        "item_id": item_velo["id"],
        "date_debut": "2026-11-01", "date_fin": "2026-11-05",
    })

    assert response.status_code == status_code


def test_lire_reservation_existante_renvoie_200(
    client: TestClient, reservation_active: dict[str, Any]
) -> None:
    response = client.get(f"/reservations/{reservation_active['id']}")

    assert response.status_code == 200
    assert response.json() == reservation_active


# Validation


@pytest.mark.parametrize(
    ("date_debut", "date_fin"),
    [
        ("2026-10-05", "2026-10-01"),  # inversées
        ("2026-10-01", "2026-10-01"),  # égales
    ],
)
def test_creer_reservation_avec_dates_invalides_renvoie_422(
    client: TestClient, item_velo: dict[str, Any],
    date_debut: str, date_fin: str
) -> None:
    response = client.post("/reservations", json={
        "item_id": item_velo["id"],
        "date_debut": date_debut, "date_fin": date_fin,
    })

    assert response.status_code == 422
    erreur = response.json()["detail"][0]
    # La règle croise deux champs : le model_validator la rattache au corps entier,
    # pas à un champ. loc vaut donc ["body"], et loc[-1] ne désignerait rien de précis.
    assert erreur["loc"] == ["body"]
    # On vérifie un mot de notre propre message, pas le préfixe ajouté par Pydantic.
    assert "date_fin" in erreur["msg"]


@pytest.mark.parametrize(
    ("payload", "champ_en_erreur"),
    [
        ({"item_id": 0, "date_debut": "2026-10-01", "date_fin": "2026-10-05"}, "item_id"),
        (
            {"item_id": 1, "date_debut": "2026-10-01", "date_fin": "2026-10-05",
             "statut": "annulee"},
            "statut",
        ),
    ],
)
def test_creer_reservation_avec_champ_invalide_renvoie_422(
    client: TestClient, payload: dict[str, Any], champ_en_erreur: str
) -> None:
    response = client.post("/reservations", json=payload)

    assert response.status_code == 422
    champs = [erreur["loc"][-1] for erreur in response.json()["detail"]]
    assert champ_en_erreur in champs


def test_lister_reservations_avec_limit_101_renvoie_422(client: TestClient) -> None:
    response = client.get("/reservations", params={"limit": 101})

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][-1] == "limit"


# Filtre


def test_filtre_item_id_ne_garde_que_les_reservations_de_cet_item(
    client: TestClient,
    reservation_active: dict[str, Any],
    alice: User,
    bob: User,
) -> None:
    # Given : une réservation sur le vélo (fixture) et une sur un second item.
    tente = client.post("/items", json={
        "titre": "Tente 2 places", "tarif_jour": 12,
    }).json()
    client.post("/reservations", json={
        "item_id": tente["id"],
        "date_debut": "2026-10-01", "date_fin": "2026-10-05",
    })

    # When : on filtre sur le vélo.
    response = client.get("/reservations", params={"item_id": reservation_active["item_id"]})

    # Then : seule la réservation du vélo est renvoyée.
    assert response.status_code == 200
    assert [reservation["id"] for reservation in response.json()] == [reservation_active["id"]]


# Ressource absente


def test_lire_reservation_inexistante_renvoie_404(client: TestClient) -> None:
    response = client.get("/reservations/999")

    assert response.status_code == 404


def test_annuler_reservation_inexistante_renvoie_404(client: TestClient) -> None:
    response = client.post("/reservations/999/annuler")

    assert response.status_code == 404


# Annulation


@pytest.mark.parametrize(
    ("client_fixture", "status_code"),
    [("raw_client", 401), ("client_alice", 200), ("client_bob", 403)],
)
def test_matrice_annulation_reservation(
    request: pytest.FixtureRequest,
    client_fixture: str,
    status_code: int,
    reservation_active: dict[str, Any],
) -> None:
    test_client = request.getfixturevalue(client_fixture)
    response = test_client.post(
        f"/reservations/{reservation_active['id']}/annuler"
    )

    assert response.status_code == status_code
    if status_code == 200:
        assert response.json()["statut"] == "annulee"


def test_un_tiers_ne_peut_pas_annuler_une_reservation(
    client_alice: TestClient,
    client_bob: TestClient,
    item_velo: dict[str, Any],
) -> None:
    reservation = client_alice.post("/reservations", json={
        "item_id": item_velo["id"],
        "date_debut": "2026-10-01", "date_fin": "2026-10-05",
    }).json()
    response = client_bob.post(f"/reservations/{reservation['id']}/annuler")

    assert response.status_code == 403
    assert client_bob.get(f"/reservations/{reservation['id']}").json()["statut"] == "active"


def test_emprunteur_et_proprietaire_peuvent_annuler_une_reservation(
    client_alice: TestClient,
    client_bob: TestClient,
    item_velo: dict[str, Any],
) -> None:
    reservation = client_bob.post("/reservations", json={
        "item_id": item_velo["id"],
        "date_debut": "2026-10-01", "date_fin": "2026-10-05",
    }).json()
    response = client_bob.post(f"/reservations/{reservation['id']}/annuler")
    assert response.status_code == 200
    assert response.json()["statut"] == "annulee"

    second_reservation = client_bob.post("/reservations", json={
        "item_id": item_velo["id"],
        "date_debut": "2026-10-10", "date_fin": "2026-10-15",
    }).json()
    response = client_alice.post(
        f"/reservations/{second_reservation['id']}/annuler"
    )

    assert response.status_code == 200
    assert response.json()["statut"] == "annulee"


def test_annuler_reservation_deja_annulee_renvoie_409(
    client: TestClient, reservation_active: dict[str, Any]
) -> None:
    # Given : la réservation a déjà été annulée.
    reservation_id = reservation_active["id"]
    client.post(f"/reservations/{reservation_id}/annuler")

    # When : on demande une seconde annulation.
    response = client.post(f"/reservations/{reservation_id}/annuler")

    # Then : l'API refuse avec un conflit, et la réservation reste annulée.
    assert response.status_code == 409
    assert client.get(f"/reservations/{reservation_id}").json()["statut"] == "annulee"


def test_patch_reservation_active_renvoie_200_avec_statut_annulee(
    client: TestClient, reservation_active: dict[str, Any]
) -> None:
    response = client.patch(
        f"/reservations/{reservation_active['id']}", json={"statut": "annulee"}
    )

    assert response.status_code == 200
    assert response.json()["statut"] == "annulee"


def test_patch_reservation_inexistante_renvoie_404(client: TestClient) -> None:
    response = client.patch("/reservations/999", json={"statut": "annulee"})

    assert response.status_code == 404


def test_patch_reservation_deja_annulee_renvoie_409(
    client: TestClient, reservation_active: dict[str, Any]
) -> None:
    reservation_id = reservation_active["id"]
    client.post(f"/reservations/{reservation_id}/annuler")

    response = client.patch(
        f"/reservations/{reservation_id}", json={"statut": "annulee"}
    )

    assert response.status_code == 409


def test_patch_reservation_avec_statut_invalide_renvoie_422(
    client: TestClient, reservation_active: dict[str, Any]
) -> None:
    response = client.patch(
        f"/reservations/{reservation_active['id']}", json={"statut": "active"}
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][-1] == "statut"


# Notification


def test_annulation_envoie_une_notification(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, reservation_active: dict[str, Any]
) -> None:
    notifier = Mock()
    monkeypatch.setattr(
        reservation_service, "envoyer_notification_annulation", notifier
    )

    response = client.post(f"/reservations/{reservation_active['id']}/annuler")

    assert response.status_code == 200
    notifier.assert_called_once_with(reservation_id=reservation_active["id"])


@pytest.mark.parametrize(
    "erreur",
    [ConnectionError("serveur mail injoignable"), TimeoutError("délai dépassé")],
    ids=["connexion", "delai"],
)
def test_annulation_reussit_meme_si_la_notification_echoue(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    reservation_active: dict[str, Any],
    erreur: Exception,
) -> None:
    # Given : la notification échoue.
    notifier = Mock(side_effect=erreur)
    monkeypatch.setattr(
        reservation_service, "envoyer_notification_annulation", notifier
    )

    # When : on annule la réservation.
    response = client.post(f"/reservations/{reservation_active['id']}/annuler")

    # Then : l'annulation est acquise malgré l'échec.
    assert response.status_code == 200
    assert response.json()["statut"] == "annulee"
    notifier.assert_called_once()


@pytest.mark.parametrize(
    ("date_debut", "date_fin", "conflit"),
    [
        (date(2026, 10, 1), date(2026, 10, 10), False),
        (date(2026, 10, 20), date(2026, 10, 30), False),
        (date(2026, 10, 5), date(2026, 10, 12), True),
        (date(2026, 10, 18), date(2026, 10, 25), True),
        (date(2026, 9, 1), date(2026, 11, 1), True),
    ],
    ids=["avant", "apres", "partiel_debut", "partiel_fin", "englobant"],
)
def test_service_refuse_les_chevauchements_et_accepte_les_autres(
    db: Session,
    item_velo: dict[str, Any],
    bob: User,
    date_debut: date,
    date_fin: date,
    conflit: bool,
) -> None:
    service = ReservationService(
        ReservationRepository(db), ItemRepository(db)
    )
    service.create(ReservationCreate(
        item_id=item_velo["id"],
        date_debut=date(2026, 10, 10), date_fin=date(2026, 10, 20),
    ), bob)

    payload = ReservationCreate(
        item_id=item_velo["id"],
        date_debut=date_debut, date_fin=date_fin,
    )
    if conflit:
        with pytest.raises(ConflitMetier):
            service.create(payload, bob)
    else:
        assert service.create(payload, bob).date_debut == date_debut


def _reservation_service(db: Session) -> ReservationService:
    return ReservationService(
        ReservationRepository(db), ItemRepository(db)
    )


def test_service_refuse_un_item_inexistant(
    db: Session, bob: User
) -> None:
    with pytest.raises(RessourceIntrouvable, match="Item 999 introuvable"):
        _reservation_service(db).create(ReservationCreate(
            item_id=999,
            date_debut=date(2026, 12, 1), date_fin=date(2026, 12, 5),
        ), bob)


def test_service_refuse_un_item_indisponible(
    db: Session, item_velo: dict[str, Any], bob: User
) -> None:
    item = db.get(Item, item_velo["id"])
    assert item is not None
    item.disponible = False

    with pytest.raises(ConflitMetier, match="indisponible"):
        _reservation_service(db).create(ReservationCreate(
            item_id=item.id,
            date_debut=date(2026, 12, 1), date_fin=date(2026, 12, 5),
        ), bob)


def test_service_refuse_annulation_d_une_reservation_non_active(
    db: Session, item_velo: dict[str, Any], bob: User
) -> None:
    service = _reservation_service(db)
    reservation = service.create(ReservationCreate(
        item_id=item_velo["id"],
        date_debut=date(2026, 12, 1), date_fin=date(2026, 12, 5),
    ), bob)
    service.cancel(reservation.id, bob)

    with pytest.raises(ConflitMetier, match="non active"):
        service.cancel(reservation.id, bob)


# Contrainte EXCLUDE en base


def test_base_refuse_une_reservation_active_chevauchante(
    db: Session,
    reservation_active: dict[str, Any],
    bob: User,
) -> None:
    reservation = Reservation(
        item_id=reservation_active["item_id"],
        borrower_id=bob.id,
        date_debut=date(2026, 10, 3),
        date_fin=date(2026, 10, 7),
    )

    with pytest.raises(IntegrityError, match="reservations_active_no_overlap"):
        with db.begin_nested():
            db.add(reservation)
            db.flush()


def test_base_accepte_un_chevauchement_apres_annulation(
    db: Session,
    reservation_active: dict[str, Any],
    bob: User,
) -> None:
    active = db.get(Reservation, reservation_active["id"])
    assert active is not None
    active.statut = "annulee"

    reservation = Reservation(
        item_id=reservation_active["item_id"],
        borrower_id=bob.id,
        date_debut=date(2026, 10, 3),
        date_fin=date(2026, 10, 7),
    )
    with db.begin_nested():
        db.add(reservation)
        db.flush()

    assert reservation.id is not None


def test_base_accepte_une_reservation_jointive(
    db: Session,
    reservation_active: dict[str, Any],
    bob: User,
) -> None:
    reservation = Reservation(
        item_id=reservation_active["item_id"],
        borrower_id=bob.id,
        date_debut=date(2026, 10, 5),
        date_fin=date(2026, 10, 8),
    )
    with db.begin_nested():
        db.add(reservation)
        db.flush()

    assert reservation.id is not None


def test_course_sur_la_contrainte_exclude_renvoie_409(
    client_bob: TestClient,
    reservation_active: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        ReservationRepository,
        "has_active_overlap",
        lambda self, item_id, date_debut, date_fin: False,
    )

    response = client_bob.post("/reservations", json={
        "item_id": reservation_active["item_id"],
        "date_debut": "2026-10-03",
        "date_fin": "2026-10-07",
    })

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Le créneau demandé est déjà réservé"
    }
    reservations = client_bob.get(
        "/reservations", params={"item_id": reservation_active["item_id"]}
    )
    assert reservations.status_code == 200
    assert len(reservations.json()) == 1
