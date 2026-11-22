from datetime import date
from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from app.api_client import ApiError, api_client
from app.auth import Token
from app.templating import templates

router = APIRouter()


def detail_error(
    request: Request,
    exc: ApiError,
    item_id: int,
    token: str | None,
) -> HTMLResponse:
    item = api_client.get_item(item_id)
    reservations = api_client.list_reservations(token, item_id) if token else []
    current_user = api_client.get_current_user(token) if token else None
    return templates.TemplateResponse(
        request,
        "items/detail.html",
        {
            "item": item,
            "reservations": reservations,
            "current_user": current_user,
            "messages": exc.messages(),
            "saisie": {},
        },
        status_code=exc.status_code,
    )


@router.post("/items/{item_id}/reservations")
def create_reservation(
    request: Request,
    item_id: int,
    token: Token,
    date_debut: Annotated[date, Form()],
    date_fin: Annotated[date, Form()],
) -> Response:
    try:
        api_client.create_reservation(token, item_id, date_debut, date_fin)
    except ApiError as exc:
        if exc.status_code not in (409, 422):
            raise
        item = api_client.get_item(item_id)
        reservations = api_client.list_reservations(token, item_id)
        current_user = api_client.get_current_user(token) if token else None
        return templates.TemplateResponse(
            request,
            "items/detail.html",
            {
                "item": item,
                "reservations": reservations,
                "current_user": current_user,
                "messages": exc.messages(),
                "saisie": {
                    "date_debut": date_debut,
                    "date_fin": date_fin,
                },
            },
            status_code=exc.status_code,
        )
    return RedirectResponse(
        f"/items/{item_id}?reservation=ok",
        status_code=303,
    )


@router.post("/reservations/{reservation_id}/cloturer")
def complete_reservation(
    request: Request,
    reservation_id: int,
    token: Token,
    item_id: Annotated[int, Form()],
) -> Response:
    try:
        api_client.complete_reservation(token, reservation_id)
    except ApiError as exc:
        if exc.status_code not in (403, 404, 409, 422):
            raise
        return detail_error(request, exc, item_id, token)
    return RedirectResponse(f"/items/{item_id}", status_code=303)


@router.post("/reservations/{reservation_id}/avis")
def create_review(
    request: Request,
    reservation_id: int,
    token: Token,
    item_id: Annotated[int, Form()],
    note: Annotated[int, Form()],
    commentaire: Annotated[str | None, Form()] = None,
) -> Response:
    try:
        api_client.create_review(
            token,
            reservation_id,
            note,
            commentaire or None,
        )
    except ApiError as exc:
        if exc.status_code not in (403, 404, 409, 422):
            raise
        return detail_error(request, exc, item_id, token)
    return RedirectResponse(f"/items/{item_id}", status_code=303)


@router.post("/reservations/{reservation_id}")
def update_reservation(
    reservation_id: int,
    token: Token,
    statut: Annotated[str, Form()],
    item_id: Annotated[int, Form()],
) -> RedirectResponse:
    try:
        api_client.update_reservation_statut(token, reservation_id, statut)
    except ApiError as exc:
        if exc.status_code != 409:
            raise
        return RedirectResponse(
            f"/items/{item_id}?annulation=deja",
            status_code=303,
        )
    return RedirectResponse(f"/items/{item_id}", status_code=303)
