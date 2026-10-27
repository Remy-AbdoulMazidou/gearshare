# GearShare

Plateforme de prêt de matériel entre étudiants. Projet du module « Fullstack data application »
(ESIEE Paris, E5 DSIA, 2026-2027).

## Lancer le projet

```bash
git clone https://github.com/Remy-AbdoulMazidou/gearshare.git
cd gearshare
cp .env.example .env
docker compose up --build
```

- Frontend : http://localhost:8080
- API : http://localhost:8000
- Documentation interactive de l'API : http://localhost:8000/docs

TP 2 de la séance 4 en cours : `items` est stocké dans PostgreSQL, `reservations` encore en
mémoire (étape 7). Tant que l'étape 6 n'est pas faite, les migrations s'appliquent à la main :

```bash
docker compose run --rm backend alembic upgrade head
```

### Lancer les tests

Depuis la racine du dépôt. Les tests tournent sur une base PostgreSQL dédiée (`TEST_DATABASE_URL`),
à créer une fois :

```bash
docker compose exec db createdb -U gearshare gearshare_test
docker compose run --rm backend pytest
docker compose run --rm backend pytest --cov=app --cov-report=term-missing
```

### Base de données du TP séance 3

```bash
cd tp-db
docker compose up -d
docker compose exec db psql -U gearshare -d gearshare
```

Les scripts de `tp-db/sql/init/` créent le schéma et le jeu de données au premier démarrage.
`docker compose down -v && docker compose up -d` repart d'une base propre.

## Organisation du dépôt

| Dossier ou fichier | Contenu |
|---|---|
| `backend/` | API FastAPI en couches (routers, services, repositories, models, schemas), migrations Alembic, tests pytest |
| `frontend/` | Application FastAPI qui sert les pages HTML (Jinja2) et appelle l'API |
| `docker-compose.yml` | Services `db`, `backend` et `frontend` |
| `tp-db/` | TP séance 3 : PostgreSQL, schéma, données, requêtes |
| `docs/` | Livrables des TP, suivi du projet, futures fonctionnalités |
| `CLAUDE.md`, `.claude/` | Instructions projet pour l'agent de code |
| `.github/copilot-instructions.md` | Instructions pour GitHub Copilot |

## Avancement

| Séance | État | Livrables |
|---|---|---|
| 1 · API FastAPI | Terminé | `backend/`, `docs/tp/seance-1/` (spec, review, prompts, plan de l'agent, review Copilot) |
| 2 · Tests | Terminé | `backend/tests/` (48 tests, couverture 100 %), `docs/tp/seance-2/` (mutations, prompts) |
| 3 · PostgreSQL | Terminé | `tp-db/` (schéma, requêtes, `MESURES.md`, schéma v2, `REVIEW-schema.md`, tests de contraintes), `docs/tp/seance-3/` (prompts Copilot) |
| 4 · Webapp | TP 1 terminé, TP 2 en cours (étapes 0 à 5) | `frontend/`, backend en couches sur PostgreSQL, `backend/alembic/`, 53 tests, `docs/review-migrations.md`, `docs/tp/seance-4/` (prompts Copilot) |

Le détail de l'avancement et des décisions est dans `docs/suivi/SUIVI.md`, et l'historique des
sessions dans `docs/suivi/journal.md`.

## Méthode de travail

- **Agent de code : Claude Code.** `CLAUDE.md` contient les instructions projet et les
  conventions du cours, l'équivalent du `.github/copilot-instructions.md` vu en cours. L'agent
  propose un plan avant de coder, et je valide chaque fichier avant qu'il soit écrit.
- **Prompts** préparés avec Claude (chat), puis exécutés par l'agent. Ils sont copiés tels
  quels dans `docs/tp/seance-N/prompts.md`.
- **GitHub Copilot** : seconde review de la ressource `reservations`, comparée à la mienne
  (`docs/tp/seance-1/review-copilot.md` et `REVIEW.md`). En séance 3, Copilot en mode Agent a
  écrit le DDL du schéma v2, que j'ai relu avec la grille du prof puis testé
  (`tp-db/REVIEW-schema.md`). En séance 4, Copilot en mode Agent a écrit le frontend étape par
  étape à partir de mes prompts (`docs/tp/seance-4/prompts.md`). J'ai validé chaque plan,
  vérifié chaque étape dans le navigateur et corrigé les traces.
- **De mon côté** : validation des specs et des plans, décisions de conception, relecture du
  code, tests manuels avec curl et dans le navigateur, tests de mutation, commits. Pour la
  séance 3, le SQL a été préparé avec Claude (chat), puis exécuté et vérifié par moi dans `psql`.

## Stack

FastAPI, Pydantic, pytest, Jinja2, httpx, SQLAlchemy 2.0, Alembic, Docker Compose, PostgreSQL 16.
JWT arrive en séance 5.
