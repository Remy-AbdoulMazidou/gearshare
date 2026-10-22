from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.api_client import api_client
from app.templating import templates

router = APIRouter()


@router.get("/items", response_class=HTMLResponse)
def list_items_page(request: Request) -> HTMLResponse:
    items = api_client.list_items()
    return templates.TemplateResponse(request, "items/list.html", {"items": items})


@router.get("/items/{item_id}", response_class=HTMLResponse)
def item_detail_page(request: Request, item_id: int) -> HTMLResponse:
    item = api_client.get_item(item_id)
    return templates.TemplateResponse(request, "items/detail.html", {"item": item})
