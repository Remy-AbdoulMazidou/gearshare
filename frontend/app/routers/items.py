from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from app.api_client import ApiError, api_client
from app.auth import Token
from app.templating import templates

router = APIRouter()


@router.get("/items/new", response_class=HTMLResponse)
def new_item_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "items/form.html",
        {"messages": [], "saisie": {}},
    )


@router.get("/items", response_class=HTMLResponse)
def list_items_page(request: Request) -> HTMLResponse:
    items = api_client.list_items()
    return templates.TemplateResponse(request, "items/list.html", {"items": items})


@router.post("/items")
def create_item(
    request: Request,
    token: Token,
    titre: str = Form(),
    description: str = Form(""),
    tarif_jour: float = Form(),
    disponible: bool = Form(False),
) -> Response:
    saisie = {
        "titre": titre,
        "description": description,
        "tarif_jour": tarif_jour,
        "disponible": disponible,
    }
    payload = {
        "titre": titre,
        "description": description or None,
        "tarif_jour": tarif_jour,
        "disponible": disponible,
    }
    try:
        item = api_client.create_item(payload, token=token)
    except ApiError as exc:
        if exc.status_code != 422:
            raise
        return templates.TemplateResponse(
            request,
            "items/form.html",
            {"messages": exc.messages(), "saisie": saisie},
            status_code=422,
        )
    return RedirectResponse(f"/items/{item['id']}", status_code=303)


@router.get("/items/{item_id}", response_class=HTMLResponse)
def item_detail_page(request: Request, item_id: int, token: Token) -> HTMLResponse:
    item = api_client.get_item(item_id)
    reservations = api_client.list_reservations(token, item_id)
    return templates.TemplateResponse(
        request,
        "items/detail.html",
        {"item": item, "reservations": reservations, "messages": [], "saisie": {}},
    )
