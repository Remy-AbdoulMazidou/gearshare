from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.templating import BASE_DIR

app = FastAPI(title="GearShare — frontend")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/", include_in_schema=False)
def home() -> RedirectResponse:
    return RedirectResponse("/items", status_code=307)
