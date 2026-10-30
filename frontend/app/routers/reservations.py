from datetime import date
from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import Response, RedirectResponse

from app.api_client import ApiError, api_client
from app.templating import templates

router = APIRouter()


@router.post("/items/{item_id}/reservations")
def create_reservation(
    request: Request,
    item_id: int,
    date_debut: Annotated[date, Form()],
    date_fin: Annotated[date, Form()],
) -> Response:
    try:
        borrower_id = 1  # TODO séance 5 : remplacé par l'utilisateur connecté, déduit du jeton
        api_client.create_reservation(item_id, borrower_id, date_debut, date_fin)
        
    except ApiError as exc:
        if exc.status_code not in (409, 422):
            raise
        item = api_client.get_item(item_id)
        reservations = api_client.list_reservations(item_id)
        return templates.TemplateResponse(
            request,
            "items/detail.html",
            {
                "item": item,
                "reservations": reservations,
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


@router.post("/reservations/{reservation_id}")
def update_reservation(
    reservation_id: int,
    statut: Annotated[str, Form()],
    item_id: Annotated[int, Form()],
) -> RedirectResponse:
    try:
        api_client.update_reservation_statut(reservation_id, statut)
    except ApiError as exc:
        if exc.status_code != 409:
            raise
        return RedirectResponse(
            f"/items/{item_id}?annulation=deja",
            status_code=303,
        )
    return RedirectResponse(f"/items/{item_id}", status_code=303)
