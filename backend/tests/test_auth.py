import re

import pytest
from fastapi.testclient import TestClient
import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import User


def test_me_avec_un_jeton_renvoie_l_utilisateur_connecte(
    client: TestClient, alice: User
) -> None:
    response = client.get("/auth/me")

    assert response.status_code == 200
    assert response.json()["id"] == alice.id
    assert response.json()["email"] == alice.email
    assert response.json()["display_name"] == alice.display_name


@pytest.mark.parametrize(
    ("client_fixture", "status_code"),
    [("raw_client", 401), ("client_alice", 200), ("client_bob", 200)],
)
def test_matrice_auth_me(
    request: pytest.FixtureRequest,
    client_fixture: str,
    status_code: int,
) -> None:
    test_client = request.getfixturevalue(client_fixture)
    response = test_client.get("/auth/me")

    assert response.status_code == status_code


@pytest.mark.parametrize("authorization", [None, "Bearer jeton-bidon"])
def test_me_sans_jeton_ou_avec_un_jeton_bidon_renvoie_401(
    raw_client: TestClient, authorization: str | None
) -> None:
    headers = {} if authorization is None else {"Authorization": authorization}
    response = raw_client.get("/auth/me", headers=headers)

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentification invalide"}
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_inscription_valide_renvoie_utilisateur_sans_mots_de_passe(
    raw_client: TestClient, db: Session
) -> None:
    response = raw_client.post(
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
    raw_client: TestClient,
) -> None:
    payload = {
        "email": "alice@esiee.fr",
        "password": "motdepasse-alice",
        "display_name": "Alice",
    }

    assert raw_client.post("/auth/register", json=payload).status_code == 201
    response = raw_client.post("/auth/register", json=payload)

    assert response.status_code == 409


def test_connexion_valide_renvoie_un_jeton_avec_l_id_utilisateur(
    raw_client: TestClient, db: Session
) -> None:
    response = raw_client.post(
        "/auth/register",
        json={
            "email": "alice@esiee.fr",
            "password": "motdepasse-alice",
            "display_name": "Alice",
        },
    )
    assert response.status_code == 201
    user = db.query(User).filter_by(email="alice@esiee.fr").one()
    response = raw_client.post(
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
    raw_client: TestClient, credentials: dict[str, str]
) -> None:
    raw_client.post(
        "/auth/register",
        json={
            "email": "alice@esiee.fr",
            "password": "motdepasse-alice",
            "display_name": "Alice",
        },
    )

    response = raw_client.post("/auth/login", data=credentials)

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
    raw_client: TestClient, field: str, value: str
) -> None:
    payload = {
        "email": "alice@esiee.fr",
        "password": "motdepasse-alice",
        "display_name": "Alice",
    }
    payload[field] = value

    response = raw_client.post("/auth/register", json=payload)

    assert response.status_code == 422
    assert field in [error["loc"][-1] for error in response.json()["detail"]]
