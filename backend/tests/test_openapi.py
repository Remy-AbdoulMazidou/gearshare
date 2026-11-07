import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.mark.parametrize(
    ("method", "path", "error_codes"),
    [
        ("get", "/items", []),
        ("post", "/items", [401]),
        ("get", "/items/{item_id}", [404]),
        ("put", "/items/{item_id}", [401, 403, 404]),
        ("patch", "/items/{item_id}", [401, 403, 404]),
        ("delete", "/items/{item_id}", [401, 403, 404]),
        ("get", "/reservations", [401]),
        ("post", "/reservations", [401, 404, 409]),
        ("get", "/reservations/{reservation_id}", [401, 404]),
        ("patch", "/reservations/{reservation_id}", [401, 403, 404, 409]),
        (
            "post",
            "/reservations/{reservation_id}/annuler",
            [401, 403, 404, 409],
        ),
        ("post", "/auth/register", [409]),
        ("post", "/auth/login", [401]),
        ("get", "/auth/me", [401]),
    ],
)
def test_openapi_documente_les_erreurs(method, path, error_codes):
    client = TestClient(app)

    openapi = client.get("/openapi.json").json()
    documented_responses = openapi["paths"][path][method]["responses"]

    for error_code in error_codes:
        assert str(error_code) in documented_responses
