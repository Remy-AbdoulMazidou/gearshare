from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.main import app
from app.models import Base, User


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    if settings.test_database_url is None:
        raise RuntimeError("TEST_DATABASE_URL doit être défini pour les tests")
    engine = create_engine(settings.test_database_url)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db(engine: Engine) -> Iterator[Session]:
    """Une session par test, dans une transaction annulée à la fin."""
    with engine.begin() as connection:
        connection.execute(
            text("TRUNCATE TABLE reservations, items, users RESTART IDENTITY CASCADE")
        )
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection, autoflush=False, autocommit=False)()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def raw_client(db: Session) -> Iterator[TestClient]:
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def client(
    db: Session, alice: User, raw_client: TestClient
) -> Iterator[TestClient]:
    raw_client.headers.update(
        {"Authorization": f"Bearer {create_access_token(alice.id)}"}
    )
    yield raw_client


@pytest.fixture
def alice(db: Session) -> User:
    user = User(
        email="alice@esiee.fr",
        display_name="Alice",
        password_hash="x",
    )
    db.add(user)
    db.flush()
    return user


@pytest.fixture
def borrower(db: Session) -> User:
    user = User(
        email="bob@esiee.fr",
        display_name="Bob",
        password_hash="x",
    )
    db.add(user)
    db.flush()
    return user


@pytest.fixture
def item_velo(client: TestClient, alice: User) -> dict[str, Any]:
    """Un item déjà créé, renvoyé tel que l'API l'expose."""
    response = client.post("/items", json={
        "titre": "Vélo de ville",
        "description": "Trois vitesses",
        "tarif_jour": 8.5,
    })
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def reservation_active(
    client: TestClient, item_velo: dict[str, Any]
) -> dict[str, Any]:
    """Une réservation active sur item_velo, renvoyée telle que l'API l'expose."""
    response = client.post("/reservations", json={
        "item_id": item_velo["id"],
        "date_debut": "2026-10-01", "date_fin": "2026-10-05",
    })
    assert response.status_code == 201
    return response.json()
