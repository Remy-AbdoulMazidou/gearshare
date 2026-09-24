# Plan — ressource `reservations` (étape 6, TP séance 1)

## Contexte

L'étape 6 du TP est l'exercice agentic : la ressource `reservations` doit être produite par
l'agent à partir d'une spécification écrite à l'avance, puis relue par Rémy dans `REVIEW.md`.
La spec est figée dans `docs/tp/seance-1/SPEC-reservations.md` et fait foi. Le but n'est pas
d'obtenir le meilleur code possible, mais du code **conforme à la spec**, dans le style de
`backend/app/routers/items.py`, pour que la review porte sur des écarts réels.

Les points que le TP annonce comme les pièges classiques d'un agent, et qui seront regardés :
validation croisée des dates dans Pydantic (et non un `if` dans le router), codes 201/404/409
exacts, `response_model` partout, aucun accès au stockage d'`items`, pas d'`async def` sans
`await`, routes littérales avant les routes paramétrées.

## Fichiers touchés

- `backend/app/schemas/reservation.py` (nouveau)
- `backend/app/routers/reservations.py` (nouveau)
- `backend/app/main.py` (2 lignes : import + `include_router`)

Aucune dépendance ajoutée : `date`, `Literal`, `model_validator` viennent de la bibliothèque
standard et de Pydantic, déjà dans `requirements.txt`.

## 1. `backend/app/schemas/reservation.py`

Calqué sur `app/schemas/item.py` : `ConfigDict(extra="forbid")` sur l'entrée (convention
`CLAUDE.md`), contraintes en `Field`.

- `ReservationCreate` : `item_id: int = Field(ge=1)`, `date_debut: date`, `date_fin: date`.
  La règle `date_fin > date_debut` ne s'exprime pas en `Field` : elle passe par un
  `@model_validator(mode="after")` qui lève une `ValueError`. FastAPI la traduit en **422**,
  et la contrainte reste attachée au schéma, donc visible dans OpenAPI.
- `ReservationRead` : `id`, `item_id`, `date_debut`, `date_fin`,
  `statut: Literal["active", "annulee"]`. Le `Literal` reprend l'énumération de la spec et
  la publie dans `/docs`, là où un `str` la perdrait.

`statut` n'est pas dans `ReservationCreate` : la spec ne le liste pas en entrée, il est donc
attribué par le serveur à `"active"` à la création.

## 2. `backend/app/routers/reservations.py`

Même structure que `items.py` : `APIRouter(prefix="/reservations", tags=["reservations"])`,
stockage `FAKE_DB: dict[int, dict]` et compteur `_next_id` **locaux au module**, donc sans
aucun lien avec ceux d'`items`. Toutes les fonctions en `def` (aucun `await`).

Ordre de déclaration — littérales d'abord, paramétrées ensuite :

| Ordre | Route | Code | Comportement |
|---|---|---|---|
| 1 | `GET ""` | 200 | `list[ReservationRead]`, filtre `item_id`, tronque à `limit` |
| 2 | `POST ""` | 201 | `ReservationRead`, `statut` forcé à `"active"` |
| 3 | `GET "/{reservation_id}"` | 200 | 404 si absente |
| 4 | `POST "/{reservation_id}/annuler"` | 200 | 404 si absente, 409 si déjà annulée |

Chemin `""` et non `"/reservations"` pour les deux premières, à cause du `prefix` — le piège
déjà rencontré à l'étape 5.

Les seuls `if` du router portent sur l'existence en base et sur le statut courant : ni l'un ni
l'autre ne peut s'exprimer dans Pydantic, qui ne voit pas le stockage. Toute la validation de
forme (bornes, dates, champs inconnus) reste dans les schémas, conformément à la spec.

`reservation_id` reçoit `Path(ge=1)`, comme `item_id` dans `items.py`.

## 3. `backend/app/main.py`

```python
from app.routers import items, reservations
...
app.include_router(reservations.router)
```

## Écarts assumés par rapport à `items.py` (tranchés par Rémy)

- **Pas de `skip`** sur `GET /reservations` : la spec énumère `item_id` et `limit`, on s'y tient.
- **Pas de schéma `ReservationUpdate`** : aucune route ne le consommerait. La règle des trois
  schémas de `CLAUDE.md` vise un CRUD complet ; l'ajouter ici produirait du code mort.

Ces deux écarts avec le gabarit d'`items` sont volontaires et à mentionner dans `REVIEW.md`.

## Vérification

1. L'API tourne avec `--reload`, aucun redémarrage nécessaire.
2. `/openapi.json` : vérifier que les 4 nouvelles opérations apparaissent sous le tag
   `reservations`, que les chemins sont bien `/reservations` et `/reservations/{reservation_id}`
   (pas de `/reservations/reservations`), et que les routes d'`items` sont inchangées.
3. Série curl, cas nominaux et cas d'erreur :
   - `POST /reservations` valide → 201, `statut: "active"`
   - `POST` avec `date_fin` <= `date_debut` → 422, erreur portée par le corps
   - `POST` avec `item_id: 0` → 422, `loc` = `["body","item_id"]`
   - `POST` avec un champ inconnu → 422, `extra_forbidden`
   - `GET /reservations` → 200 ; `?item_id=…` filtre ; `?limit=500` → 422
   - `GET /reservations/1` → 200 ; `/999` → 404 ; `/0` → 422
   - `POST /reservations/1/annuler` → 200, `statut: "annulee"`
   - même appel une seconde fois → **409**
   - `POST /reservations/999/annuler` → **404** (point de contrôle explicite du TP)
4. Contrôle d'isolement : `grep -n "items" backend/app/routers/reservations.py` doit ne rien
   renvoyer.

## Hors périmètre

`REVIEW.md` est un livrable de Rémy (`CLAUDE.md`). Je peux préparer le tableau vide avec les
huit points de contrôle du TP, sans en remplir aucune ligne. Aucun commit.
