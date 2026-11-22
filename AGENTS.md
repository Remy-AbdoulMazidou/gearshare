# Projet

GearShare, application Python Fullstack de prêt de matériel entre étudiants.
Tout se fait en français.

# Stack

- Backend : Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic.
- Base : PostgreSQL 16.
- Frontend : application Python séparée, passant uniquement par l'API REST.
- Docker Compose.

# Arborescence

- backend/app/ : main.py, routers, schemas, services, repositories, models, core, api, db.
- backend/alembic/ : migrations Alembic.
- backend/tests/ : tests pytest.
- frontend/app/ : application frontend séparée.

# Commandes

- Démarrer : docker compose up.
- Tests : docker compose run --rm backend pytest.
- Lint : docker run --rm -v "$PWD":/src -w /src python:3.12-slim sh -c "pip install -q ruff==0.17.3 && ruff check backend frontend".
- Créer une migration : docker compose run --rm backend alembic revision --autogenerate -m "<description>".
- Appliquer les migrations : docker compose run --rm migrate.

# Conventions

- La logique métier vit dans les services.
- Les routers n'accèdent jamais aux données, ils passent par les services.
- Erreurs métier traduites par le gestionnaire d'erreurs de backend/app/main.py.
- La validation des entrées vit dans Pydantic.
- PATCH utilise model_dump(exclude_unset=True).
- Codes HTTP : 201, 204, 401, 403, 404, 409, 422. Aucun 500 volontaire.
- Noms de tests : test_ac_<story>_<critère>_... .
- Une migration autogenerate est toujours relue.
- Tests sur la base gearshare_test. Fixtures alice, bob, client_alice et client_bob dans
  backend/tests/conftest.py. Au moins un test par critère d'acceptation.
- Une feature vit dans docs/features/<nom>/ : fiche.md, plan.md, prompts.md. Modèles dans
  docs/templates/.
- À la fin de chaque étape, donner 3 à 5 points « À savoir expliquer » sur le code produit.

# Interdits

- Aucun secret dans le code, uniquement des variables d'environnement.
- Ne jamais modifier une migration déjà appliquée.
- Toujours tirer l'identité du jeton, jamais du corps de la requête.
- Ne jamais lancer git commit ni git push.

# Traces

- Copier les prompts tels quels dans prompts.md.
- Dans docs/suivi/journal.md, l'agent écrit son propre nom (ex. GitHub Copilot (mode Agent)).
- Ne noter dans « Vérifié » que les vérifications réellement réussies.
- Mettre à jour docs/suivi/SUIVI.md et docs/suivi/journal.md à la fin d'une tâche.
- Les fichiers de review et docs/retour-experience.md sont écrits par Rémy.
