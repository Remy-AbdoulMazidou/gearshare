# GearShare

Plateforme de prêt de matériel entre étudiants. Projet du module « Fullstack data application »
(ESIEE Paris, E5 DSIA, 2026-2027).

## Lancer le projet

```bash
git clone <url-du-repo>
cd gearshare/backend
docker compose up --build
```

- API : http://localhost:8000
- Documentation interactive : http://localhost:8000/docs

> La commande de lancement passera à la racine du dépôt quand le frontend et PostgreSQL
> arriveront (séance 4).

## Organisation du dépôt

| Dossier | Contenu |
|---|---|
| `backend/` | API FastAPI |
| `docs/` | Documentation : livrables des TP, fonctionnalités, suivi du projet |
| `CLAUDE.md` | Instructions projet pour l'agent de code |

## Stack

FastAPI, Pydantic, pytest, Docker Compose. PostgreSQL, SQLAlchemy, Alembic, frontend et JWT
arrivent au fil des séances.
