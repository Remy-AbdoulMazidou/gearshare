# GearShare

Plateforme de prêt de matériel entre étudiants. Projet du module « Fullstack data application »
(ESIEE Paris, E5 DSIA, 2026-2027).

## Lancer le projet

```bash
git clone https://github.com/Remy-AbdoulMazidou/gearshare.git
cd gearshare
docker compose up --build
```

- API : http://localhost:8000
- Documentation interactive : http://localhost:8000/docs

### Lancer les tests

Depuis la racine du dépôt :

```bash
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
| `backend/` | API FastAPI et ses tests pytest |
| `tp-db/` | TP séance 3 : PostgreSQL, schéma, données, requêtes |
| `docs/` | Livrables des TP, suivi du projet, futures fonctionnalités |
| `CLAUDE.md`, `.claude/` | Instructions projet pour l'agent de code |

## Avancement

| Séance | État | Livrables |
|---|---|---|
| 1 · API FastAPI | Terminé | `backend/`, `docs/tp/seance-1/` (spec, review, prompts, plan de l'agent, review Copilot) |
| 2 · Tests | Terminé | `backend/tests/` (48 tests, couverture 100 %), `docs/tp/seance-2/` (mutations, prompts) |
| 3 · PostgreSQL | Terminé | `tp-db/` (schéma, requêtes, `MESURES.md`, schéma v2, `REVIEW-schema.md`, tests de contraintes), `docs/tp/seance-3/` (prompts Copilot) |

Le détail de l'avancement et des décisions est dans `docs/suivi/SUIVI.md`, et l'historique des
sessions dans `docs/suivi/journal.md`.

## Méthode de travail

- **Agent de code : Claude Code.** `CLAUDE.md` contient les instructions projet et les
  conventions du cours, l'équivalent du `.github/copilot-instructions.md` vu en cours. L'agent
  propose un plan avant de coder, et je valide chaque fichier avant qu'il soit écrit.
- **Prompts** préparés avec Claude (chat), puis exécutés par Claude Code. Ils sont copiés tels
  quels dans `docs/tp/seance-N/prompts.md`.
- **GitHub Copilot** : seconde review de la ressource `reservations`, comparée à la mienne
  (`docs/tp/seance-1/review-copilot.md` et `REVIEW.md`). En séance 3, Copilot en mode Agent a
  écrit le DDL du schéma v2, que j'ai relu avec la grille du prof puis testé
  (`tp-db/REVIEW-schema.md`).
- **De mon côté** : validation des specs et des plans, décisions de conception, relecture du
  code, tests manuels avec curl, tests de mutation, commits. Pour la séance 3, le SQL a été
  préparé avec Claude (chat), puis exécuté et vérifié par moi dans `psql`.

## Stack

FastAPI, Pydantic, pytest, Docker Compose, PostgreSQL 16. SQLAlchemy, Alembic, frontend et JWT
arrivent au fil des séances.
