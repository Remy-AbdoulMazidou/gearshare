from typing import Any

import pytest
from fastapi.testclient import TestClient

from tests.conftest import Storage


def _item(item_id: int, titre: str = "Item", disponible: bool = True) -> dict[str, Any]:
    return {"id": item_id, "titre": titre, "description": None,
            "tarif_jour": 5.0, "disponible": disponible}


# Cas nominaux


def test_creer_item_renvoie_201_avec_un_id(client: TestClient) -> None:
    response = client.post("/items", json={"titre": "Tente 2 places", "tarif_jour": 12})

    assert response.status_code == 201
    corps = response.json()
    assert corps["id"] == 1
    assert corps["titre"] == "Tente 2 places"
    assert corps["disponible"] is True


def test_lire_item_existant_renvoie_200(client: TestClient, item_velo: dict[str, Any]) -> None:
    response = client.get(f"/items/{item_velo['id']}")

    assert response.status_code == 200
    assert response.json() == item_velo


def test_lister_sans_item_renvoie_liste_vide(client: TestClient) -> None:
    response = client.get("/items")

    assert response.status_code == 200
    assert response.json() == []


def test_remplacer_item_remplace_tous_les_champs(
    client: TestClient, item_velo: dict[str, Any]
) -> None:
    # When : PUT sans description, alors que l'item en avait une.
    response = client.put(
        f"/items/{item_velo['id']}", json={"titre": "Vélo pliant", "tarif_jour": 10}
    )

    # Then : la description repart à sa valeur par défaut, comme à la création.
    assert response.status_code == 200
    corps = response.json()
    assert corps["titre"] == "Vélo pliant"
    assert corps["description"] is None


def test_supprimer_item_renvoie_204_sans_corps(
    client: TestClient, item_velo: dict[str, Any]
) -> None:
    response = client.delete(f"/items/{item_velo['id']}")

    assert response.status_code == 204
    assert response.content == b""


# Validation


@pytest.mark.parametrize(
    ("payload", "champ_en_erreur"),
    [
        ({"titre": "ab", "tarif_jour": 8.5}, "titre"),                          # trop court
        ({"titre": "a" * 121, "tarif_jour": 8.5}, "titre"),                     # trop long
        ({"titre": "Vélo", "description": "a" * 1001, "tarif_jour": 8.5}, "description"),
        ({"titre": "Vélo de ville", "tarif_jour": 0}, "tarif_jour"),            # nul
        ({"titre": "Vélo de ville", "tarif_jour": -3}, "tarif_jour"),           # négatif
        ({"titre": "Vélo de ville"}, "tarif_jour"),                             # manquant
        ({"titre": "Vélo de ville", "tarif_jour": 8.5, "couleur": "rouge"}, "couleur"),
    ],
)
def test_creer_item_invalide_renvoie_422(
    client: TestClient, payload: dict[str, Any], champ_en_erreur: str
) -> None:
    response = client.post("/items", json=payload)

    assert response.status_code == 422
    champs = [erreur["loc"][-1] for erreur in response.json()["detail"]]
    assert champ_en_erreur in champs


@pytest.mark.parametrize(
    ("payload", "champ_en_erreur"),
    [
        ({"titre": "ab"}, "titre"),
        ({"tarif_jour": 0}, "tarif_jour"),
        ({"couleur": "rouge"}, "couleur"),
    ],
)
def test_modifier_item_invalide_renvoie_422(
    client: TestClient, item_velo: dict[str, Any], payload: dict[str, Any], champ_en_erreur: str
) -> None:
    response = client.patch(f"/items/{item_velo['id']}", json=payload)

    assert response.status_code == 422
    champs = [erreur["loc"][-1] for erreur in response.json()["detail"]]
    assert champ_en_erreur in champs


@pytest.mark.parametrize(
    ("params", "champ_en_erreur"),
    [
        ({"skip": -1}, "skip"),
        ({"limit": 0}, "limit"),
        ({"limit": 101}, "limit"),
    ],
)
def test_lister_items_avec_parametres_invalides_renvoie_422(
    client: TestClient, params: dict[str, int], champ_en_erreur: str
) -> None:
    response = client.get("/items", params=params)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][-1] == champ_en_erreur


def test_lire_item_avec_id_nul_renvoie_422(client: TestClient) -> None:
    response = client.get("/items/0")

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][-1] == "item_id"


# Ressource absente


def test_lire_item_inexistant_renvoie_404(client: TestClient) -> None:
    response = client.get("/items/999")

    assert response.status_code == 404


def test_remplacer_item_inexistant_renvoie_404(client: TestClient) -> None:
    response = client.put("/items/999", json={"titre": "Vélo pliant", "tarif_jour": 10})

    assert response.status_code == 404


def test_modifier_item_inexistant_renvoie_404(client: TestClient) -> None:
    response = client.patch("/items/999", json={"titre": "Vélo pliant"})

    assert response.status_code == 404


def test_supprimer_item_inexistant_renvoie_404(client: TestClient) -> None:
    response = client.delete("/items/999")

    assert response.status_code == 404


# Effets de bord et cas limites


def test_patch_partiel_conserve_les_autres_champs(
    client: TestClient, item_velo: dict[str, Any]
) -> None:
    # When : on ne modifie que le tarif.
    response = client.patch(f"/items/{item_velo['id']}", json={"tarif_jour": 12})

    # Then : le tarif change, le reste de l'item est intact.
    assert response.status_code == 200
    assert response.json() == {**item_velo, "tarif_jour": 12}


def test_item_supprime_n_est_plus_lisible(client: TestClient, item_velo: dict[str, Any]) -> None:
    # Given : l'item a été supprimé.
    client.delete(f"/items/{item_velo['id']}")

    # When : on essaie de le relire.
    response = client.get(f"/items/{item_velo['id']}")

    # Then : il n'existe plus.
    assert response.status_code == 404


def test_filtre_q_ignore_la_casse(client: TestClient, storage: Storage) -> None:
    # Given : deux items, un seul contient « vélo » dans son titre.
    storage.items[1] = _item(1, titre="Vélo de ville")
    storage.items[2] = _item(2, titre="Tente 2 places")

    # When : on cherche en majuscules.
    response = client.get("/items", params={"q": "VÉLO"})

    # Then : seul le vélo est renvoyé.
    assert [item["id"] for item in response.json()] == [1]


def test_filtre_disponible_ne_garde_que_les_items_correspondants(
    client: TestClient, storage: Storage
) -> None:
    # Given : un item disponible, un item indisponible.
    storage.items[1] = _item(1, disponible=True)
    storage.items[2] = _item(2, disponible=False)

    # When : on ne demande que les indisponibles.
    response = client.get("/items", params={"disponible": False})

    # Then : seul l'item indisponible est renvoyé.
    assert [item["id"] for item in response.json()] == [2]


def test_lister_avec_skip_et_limit_renvoie_la_bonne_tranche(
    client: TestClient, storage: Storage
) -> None:
    # Given : cinquante items, insérés sans passer par cinquante requêtes HTTP.
    for i in range(1, 51):
        storage.items[i] = _item(i, titre=f"Item {i}")

    response = client.get("/items", params={"skip": 40, "limit": 20})

    assert [item["id"] for item in response.json()] == list(range(41, 51))


def test_lister_sans_limit_renvoie_20_items_au_plus(client: TestClient, storage: Storage) -> None:
    # Given : trente items.
    for i in range(1, 31):
        storage.items[i] = _item(i, titre=f"Item {i}")

    response = client.get("/items")

    assert [item["id"] for item in response.json()] == list(range(1, 21))
