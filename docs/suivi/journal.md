# Journal des sessions

Une entrée par session de travail, la plus récente en bas.

## 2026-09-23 · Initialisation

- Fait par : Rémy
- Création du dépôt à partir du `projet-demo` de la séance 1.
- Mise en place de `CLAUDE.md`, du suivi (`docs/suivi/`) et des commandes `/reprendre` et `/cloturer`.

## 2026-09-24 · TP séance 1, étapes 1 à 4

- Fait par : Claude Code pour le code, Rémy pour les tests et les commits.
- Étape 1 : route `GET /items/{item_id}` avec `Path(ge=1)`.
- Étape 2 : route `GET /items` avec `skip`, `limit` (plafonné à 100), `q` et `disponible`.
- Étape 3 : `app/schemas/item.py` (`ItemCreate`, `ItemRead`) avec `extra="forbid"`,
  stockage `FAKE_DB` en mémoire et `POST /items` en 201.
- Étape 4 : `ItemUpdate`, filtres et pagination réels sur `GET /items`, `GET`/`PUT`/`PATCH`
  unitaires avec 404, `DELETE` en 204 sans corps.
- Quatre commits, un par étape. Étapes 5 et 6 volontairement non faites.
- Problème rencontré : le TP laisse entendre que `disponible=oui` est accepté comme booléen.
  En réalité Pydantic v2 n'accepte que les valeurs anglaises (`true`, `yes`, `on`, `1`,
  `false`, `no`, `off`, `0`) ; `oui` renvoie donc 422, comme `peut-etre`.
- Vérification faite par Rémy : `exclude_unset=True` retiré du `PATCH` pour observer le bug,
  la `description` était bien écrasée à `null`, puis remis en place.
- Corrections de Rémy : aucune sur le code, l'arbre de travail committé est identique à ce qui
  a été produit. Seul le message du commit de l'étape 1 a été reformulé.

## 2026-09-24 · TP séance 1, étapes 5 et 6

- Fait par : Rémy pour les tests, les décisions et les commits ; Claude Code pour le code.
  Review : vérifications, tests et décisions faits par Rémy, texte mis en forme avec l'aide
  de Claude.
- Étape 5 : routes `items` déplacées dans `app/routers/items.py` derrière un
  `APIRouter(prefix="/items", tags=["items"])`, avec `FAKE_DB` et `_next_id`. `main.py` réduit
  à la création de l'app, `include_router` et `/health`. Refactoring vérifié en comparant
  `/openapi.json` avant et après : chemins, paramètres et codes identiques, seuls les `tags`
  changent.
- Étape 6 : `docs/tp/seance-1/SPEC-reservations.md` reprend le modèle donné dans le TP, relue
  et validée par Rémy ; puis ressource `reservations` générée par Claude Code en mode Plan
  (schéma, router, branchement).
  Validation croisée des dates par `model_validator(mode="after")`, 409 sur double annulation.
- Traces du TP : `plan-agent.md`, `prompts.md` et `REVIEW.md` dans `docs/tp/seance-1/`.
- L'agent a posé deux questions avant de coder (`ReservationUpdate`, `skip`) plutôt que de
  trancher seul. Réponses de Rémy : ne pas créer le schéma, ne pas ajouter `skip`.
- Points relevés, non corrigés car hors spec : 404 et 409 n'apparaissent pas dans `/docs`
  faute de `responses=` sur les routes ; l'erreur de dates renvoie `loc: ["body"]` sans nom de
  champ, à prendre en compte pour les tests de la séance 2.
- Corrections de Rémy : aucune sur le code, d'après `REVIEW.md`. Le `ge=1` ajouté par l'agent sur
  le filtre `item_id` de la liste a été gardé, bien que la spec ne le demandait pas.
- Correction faite pendant la clôture : la ligne « Décisions » du 2026-09-24 disait que
  `FAKE_DB` était dans `main.py`, ce qui n'est plus vrai depuis l'étape 5.

## 2026-09-26 · TP séance 2, étape 1

- Fait par : Claude Code pour le code, Rémy pour la validation du plan et les décisions.
- `pytest==8.3.3`, `pytest-cov==5.0.0` et `httpx==0.27.2` ajoutés à `requirements.txt`, avec les
  mêmes versions que le projet-demo.
- `pytest.ini`, `tests/__init__.py` et `tests/test_health.py` copiés du projet-demo.
- `Dockerfile` : `COPY tests` et `COPY pytest.ini`. `docker-compose.yml` : volumes sur `tests/`
  et `pytest.ini`, pour que les tests soient pris en compte sans refaire le build.
  Le Dockerfile du demo ne copie pas `tests/`, d'où l'adaptation.
- `_next_id` global remplacé par une fonction `_next_id()` dans les deux routers.
- Vérifié : `docker compose run --rm api pytest` donne 1 test vert ; API démarrée, ids 1, 2, 3,
  suppression du 3, le `POST` suivant redonne 3.
- Problème relevé, non corrigé : avertissement de dépréciation `anyio.abc.BlockingPortal`, qui
  vient de `starlette`, car `anyio` n'est pas épinglé. Sans effet sur les tests.
- Prompt copié dans `docs/tp/seance-2/prompts.md`.

## 2026-09-26 · TP séance 2, étape 2

- Fait par : Claude Code pour le code, Rémy pour la validation du plan et des deux choix.
- `tests/conftest.py` : dataclass `Storage` avec `reset_all()`, fixtures `storage`, `client`
  (qui dépend de `storage`) et `item_velo`, sans `autouse`, comme dans les sections 3.4 et 3.5.
- `test_health.py` passe par la fixture `client`.
- `tests/test_items.py` : 29 tests (dont 13 cas en `parametrize`). Cas nominaux, 422 avec
  `loc[-1]` sur création, `PATCH`, query et path, un 404 par `raise` du router, `PATCH` partiel,
  `DELETE` puis `GET`, filtres `q` et `disponible`, pagination préparée par `storage`.
- Vérifié : 30 tests verts ; un test seul passe aussi avec `-k` ; couverture totale 81 %,
  `routers/items.py` à 100 %, `routers/reservations.py` à 39 % (pas encore testé).
- Contrôle : retrait de `exclude_unset=True` sur une copie dans le conteneur, le test
  `test_patch_partiel_conserve_les_autres_champs` passe au rouge comme attendu.
- Prompt copié dans `docs/tp/seance-2/prompts.md` (Prompt 2).
