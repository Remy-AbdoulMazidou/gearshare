from typing import Any

import pytest
from fastapi.testclient import TestClient


# Cas nominaux


def test_creer_reservation_renvoie_201_avec_statut_active(
    client: TestClient, item_velo: dict[str, Any]
) -> None:
    response = client.post("/reservations", json={
        "item_id": item_velo["id"], "date_debut": "2026-10-01", "date_fin": "2026-10-05",
    })

    assert response.status_code == 201
    corps = response.json()
    assert corps["id"] == 1
    assert corps["item_id"] == item_velo["id"]
    assert corps["statut"] == "active"


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
    client: TestClient, item_velo: dict[str, Any], date_debut: str, date_fin: str
) -> None:
    response = client.post("/reservations", json={
        "item_id": item_velo["id"], "date_debut": date_debut, "date_fin": date_fin,
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
    client: TestClient, reservation_active: dict[str, Any]
) -> None:
    # Given : une réservation sur le vélo (fixture) et une sur un second item.
    tente = client.post("/items", json={"titre": "Tente 2 places", "tarif_jour": 12}).json()
    client.post("/reservations", json={
        "item_id": tente["id"], "date_debut": "2026-10-01", "date_fin": "2026-10-05",
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


def test_annuler_reservation_active_renvoie_200_avec_statut_annulee(
    client: TestClient, reservation_active: dict[str, Any]
) -> None:
    response = client.post(f"/reservations/{reservation_active['id']}/annuler")

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
