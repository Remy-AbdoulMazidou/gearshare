from pydantic import BaseModel


class ErreurRead(BaseModel):
    detail: str


ERREUR_401 = {
    401: {
        "model": ErreurRead,
        "description": "Authentification requise ou invalide",
    }
}
ERREUR_403 = {
    403: {
        "model": ErreurRead,
        "description": "Accès refusé",
    }
}
ERREUR_404 = {
    404: {
        "model": ErreurRead,
        "description": "Ressource introuvable",
    }
}
ERREUR_409 = {
    409: {
        "model": ErreurRead,
        "description": "Conflit",
    }
}
