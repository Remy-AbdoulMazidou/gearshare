# Prompts, lint et CI

Contexte : le prof attend « lint, tests et build vérifiés avant chaque PR ». Le dépôt n'a ni linter configuré ni CI.

1. Crée ruff.toml à la racine : line-length = 100, target-version = "py312", extend-exclude = ["backend/alembic/versions"], règles E, F, W, I, B, UP, et known-first-party = ["app"] pour isort. Ne corrige pas le code existant, je le ferai moi-même.

2. Crée .github/workflows/ci.yml, déclenché sur pull_request et sur push vers main, avec trois jobs :
   - lint : Python 3.12, pip install ruff==0.17.3, ruff check backend frontend ;
   - tests : service postgres:16 (utilisateur, mot de passe et base gearshare, healthcheck pg_isready), création de la base gearshare_test avec createdb, puis dans backend/ : pip install -r requirements.txt, alembic upgrade head, alembic check, pytest -q. Variables DATABASE_URL, TEST_DATABASE_URL (hôte localhost) et JWT_SECRET avec une valeur de test au niveau du job, pas de secret réel ;
   - build : cp .env.example .env puis docker compose build.

3. Dans le README, ajoute une courte section « Qualité » : ce que vérifie la CI, et comment lancer ruff en local sans l'installer :
   docker run --rm -v "$PWD":/src -w /src python:3.12-slim sh -c "pip install -q ruff==0.17.3 && ruff check backend frontend"

4. Ajoute ce prompt tel quel dans docs/qualite/prompts.md (crée le fichier, titre « Prompts, lint et CI »).

Pas de commentaire inutile dans le YAML. Ne modifie pas docs/suivi/. Pas de commit.
