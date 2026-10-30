# Backend GearShare

API FastAPI organisée en couches :

| Dossier | Rôle |
|---|---|
| `app/routers/` | Routes HTTP : schéma en entrée, appel au service, schéma en sortie |
| `app/services/` | Règles métier, exceptions métier (`app/core/exceptions.py`) |
| `app/repositories/` | Requêtes SQLAlchemy, jamais de `commit()` |
| `app/models/` | Modèles SQLAlchemy (`users`, `items`, `reservations`) |
| `app/schemas/` | Schémas Pydantic de création, de modification et de lecture |
| `app/core/`, `app/db/`, `app/api/` | Configuration, sécurité (hachage, JWT), session SQLAlchemy, dépendances `get_db` et `get_current_user` |
| `alembic/` | Migrations du schéma |
| `tests/` | Tests pytest sur la base `gearshare_test` |

Le lancement, les migrations et les tests se font depuis la racine du dépôt : voir le
[README principal](../README.md).
