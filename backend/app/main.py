from fastapi import FastAPI, Path, Query

from app.schemas.item import ItemCreate, ItemRead

app = FastAPI(title="GearShare API", version="0.1.0")

FAKE_DB: dict[int, dict] = {}
_next_id = 1


@app.get("/health", tags=["monitoring"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/items")
def list_items(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    q: str | None = None,
    disponible: bool | None = None,
):
    return {"skip": skip, "limit": limit, "q": q, "disponible": disponible}


@app.post("/items", response_model=ItemRead, status_code=201)
def create_item(payload: ItemCreate):
    global _next_id
    item = {"id": _next_id, **payload.model_dump()}
    FAKE_DB[_next_id] = item
    _next_id += 1
    return item


@app.get("/items/{item_id}")
def get_item(item_id: int = Path(ge=1)):
    return {"item_id": item_id}
