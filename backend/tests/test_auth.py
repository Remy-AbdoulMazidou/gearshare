import re

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User


def test_inscription_valide_renvoie_utilisateur_sans_mots_de_passe(
    client: TestClient, db: Session
) -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": "alice@esiee.fr",
            "password": "motdepasse-alice",
            "display_name": "Alice",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "alice@esiee.fr"
    assert body["display_name"] == "Alice"
    assert "password" not in body
    assert "password_hash" not in body

    user = db.query(User).filter_by(email="alice@esiee.fr").one()
    assert re.fullmatch(
        r"pbkdf2_sha256\$600000\$[0-9a-f]{32}\$[0-9a-f]+",
        user.password_hash,
    )


def test_inscription_deux_fois_avec_le_meme_email_renvoie_409(
    client: TestClient,
) -> None:
    payload = {
        "email": "alice@esiee.fr",
        "password": "motdepasse-alice",
        "display_name": "Alice",
    }

    assert client.post("/auth/register", json=payload).status_code == 201
    response = client.post("/auth/register", json=payload)

    assert response.status_code == 409


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("email", "pas-un-email"),
        ("password", "1234"),
        ("password", "a" * 200),
    ],
)
def test_inscription_invalide_renvoie_422(
    client: TestClient, field: str, value: str
) -> None:
    payload = {
        "email": "alice@esiee.fr",
        "password": "motdepasse-alice",
        "display_name": "Alice",
    }
    payload[field] = value

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 422
    assert field in [error["loc"][-1] for error in response.json()["detail"]]
