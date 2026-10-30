import re

import pytest
from fastapi.testclient import TestClient
import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
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


def test_connexion_valide_renvoie_un_jeton_avec_l_id_utilisateur(
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
    user = db.query(User).filter_by(email="alice@esiee.fr").one()
    response = client.post(
        "/auth/login",
        data={"username": user.email, "password": "motdepasse-alice"},
    )

    payload = jwt.decode(
        response.json()["access_token"], settings.jwt_secret, algorithms=["HS256"]
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["expires_in"] == settings.jwt_expire_minutes * 60
    assert payload["sub"] == str(user.id)


@pytest.mark.parametrize(
    "credentials",
    [
        {"username": "alice@esiee.fr", "password": "mauvais-mot-de-passe"},
        {"username": "inconnu@esiee.fr", "password": "motdepasse-alice"},
    ],
)
def test_connexion_invalide_renvoie_la_meme_erreur(
    client: TestClient, credentials: dict[str, str]
) -> None:
    client.post(
        "/auth/register",
        json={
            "email": "alice@esiee.fr",
            "password": "motdepasse-alice",
            "display_name": "Alice",
        },
    )

    response = client.post("/auth/login", data=credentials)

    assert response.status_code == 401
    assert response.json() == {"detail": "Email ou mot de passe incorrect"}
    assert response.headers["WWW-Authenticate"] == "Bearer"


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
