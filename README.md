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

Au démarrage, le service `migrate` applique les migrations Alembic avant le lancement de l'API
(voir `docs/choix-migrations.md`). Pour appliquer une nouvelle migration pendant le développement :

```bash
docker compose run --rm migrate
```

Pour publier un objet ou réserver, créez un compte sur http://localhost:8080/inscription, puis
connectez-vous. La consultation de la liste et du détail des objets reste publique.

Dans `.env`, remplacez la valeur factice de `JWT_SECRET` par un secret aléatoire :

```bash
openssl rand -hex 32
```

### Lancer les tests

Depuis la racine du dépôt. Les tests tournent sur la base PostgreSQL `gearshare_test`
(`TEST_DATABASE_URL`), créée automatiquement au premier démarrage par `db/init/` :

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
| `backend/` | API FastAPI en couches (routers, services, repositories, models, schemas), migrations Alembic, tests pytest |
| `frontend/` | Application FastAPI qui sert les pages HTML (Jinja2) et appelle l'API |
| `docker-compose.yml` | Services `db`, `migrate` (migrations Alembic), `backend` et `frontend` |
| `db/init/` | Création de la base de test `gearshare_test` au premier démarrage |
| `tp-db/` | TP séance 3 : PostgreSQL, schéma, données, requêtes |
| `docs/` | Livrables des TP, fonctionnalités ajoutées, suivi du projet (index dans `docs/README.md`) |
| `CLAUDE.md`, `.claude/` | Instructions projet pour l'agent de code |
| `.github/copilot-instructions.md` | Instructions pour GitHub Copilot |

## Avancement

| Séance | État | Livrables |
|---|---|---|
| 1 · API FastAPI | Terminé | `backend/`, `docs/tp/seance-1/` (spec, review, prompts, plan de l'agent, review Copilot) |
| 2 · Tests | Terminé | `backend/tests/` (48 tests, couverture 100 %), `docs/tp/seance-2/` (mutations, prompts) |
| 3 · PostgreSQL | Terminé | `tp-db/` (schéma, requêtes, `MESURES.md`, schéma v2, `REVIEW-schema.md`, tests de contraintes), `docs/tp/seance-3/` (prompts Copilot) |
| 4 · Webapp | Terminé (TP 1 et TP 2) | `frontend/`, backend en couches sur PostgreSQL, `backend/alembic/`, 62 tests, `docs/review-migrations.md`, `docs/choix-migrations.md`, `docs/review-couches.md`, `docs/cas-tests-chevauchement.md`, `docs/tp/seance-4/` (prompts Copilot) |
| 5 · Authentification | Terminé | Inscription, connexion JWT, routes protégées, propriété (403), 100 tests, connexion dans le frontend, `docs/tp/seance-5/` (prompts Copilot, relecture finale) |

| Fonctionnalité ajoutée | État | Livrables |
|---|---|---|
| 01 · Pas de double réservation | Contrainte en base faite | Vérification dans le service (séance 4) et contrainte `EXCLUDE` en migration Alembic, 104 tests, course testée entre deux sessions `psql`, `docs/features/01-pas-de-double-reservation/` |

Le détail de l'avancement et des décisions est dans `docs/suivi/SUIVI.md`, et l'historique des
sessions dans `docs/suivi/journal.md`.

## Méthode de travail

- **Agents de code.** Séances 1 et 2 : Claude Code, avec les instructions projet de `CLAUDE.md`
  et les commandes `/reprendre` et `/cloturer` de `.claude/`. À partir de la séance 3 : GitHub
  Copilot en mode Agent, avec `.github/copilot-instructions.md` qui renvoie aux mêmes conventions.
- **Prompts** préparés avec Claude (chat), puis donnés à l'agent. Ils sont copiés tels quels dans
  `docs/tp/seance-N/prompts.md` et `docs/features/*/prompts.md`.
- **Reviews.** En séance 1, review de la ressource `reservations` par moi puis par Copilot, et
  comparaison (`docs/tp/seance-1/REVIEW.md` et `review-copilot.md`). Ensuite, chaque étape écrite
  par l'agent est relue et testée avant le commit. Mes corrections sont notées dans
  `docs/suivi/journal.md` (« Fait par Rémy »).
- **De mon côté** : décisions de conception, relecture du code généré, tests manuels avec curl,
  le navigateur et `psql`, tests de mutation, expériences (migrations, failles JWT, course entre
  deux transactions), commits. Pour la séance 3, le SQL a été préparé avec Claude (chat), puis
  exécuté et vérifié par moi dans `psql`. Les documents mis en forme avec Claude le disent en
  première ligne.

## Stack

FastAPI, Pydantic, pytest, Jinja2, httpx, SQLAlchemy 2.0, Alembic, Docker Compose, PostgreSQL 16,
PyJWT (HS256), mots de passe hachés en PBKDF2-HMAC-SHA256.
