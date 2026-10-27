# Suivi du projet

Dernière mise à jour : 2026-10-27

## En cours

TP 2 de la séance 4, étapes 0 à 5 terminées : backend en couches pour `items`, PostgreSQL et
Alembic, tests sur une base PostgreSQL de test (53 tests verts), N+1 corrigé.

## Prochaine étape

TP 2 de la séance 4, étape 6 : Compose à trois services, migrations appliquées au démarrage
(`docs/choix-migrations.md`), frontend branché sur la vraie base.

## Avancement des séances

- [ ] Séance 0 · Docker (optionnelle)
- [x] Séance 1 · API FastAPI
  - [x] Projet initialisé à partir du `projet-demo`
  - [x] Étapes 1 à 4 : path/query params, schémas, CRUD `items`
  - [x] Étape 5 : découpage en routers
  - [x] Étape 6 : `reservations` générée par agent, `SPEC-reservations.md`, `REVIEW.md`
  - [x] Seconde review avec GitHub Copilot (`review-copilot.md`, comparaison dans `REVIEW.md`)
- [x] Séance 2 · Tests pytest
  - [x] Étape 1 : pytest dans le conteneur, `test_health.py`, compteurs globaux supprimés
  - [x] Étape 2 : `conftest.py` (`Storage`, `storage`, `client`, `item_velo`), `test_items.py`
  - [x] Étape 3 : `reservation_active`, `test_reservations.py`, `test_schemas.py`
  - [x] Étape 4 : notification d'annulation, tests avec `monkeypatch` et `Mock`
  - [x] Mutations (cours section 8) : lancées par Rémy, `MUTATIONS.md` mis en forme avec Claude chat
- [x] Séance 3 · PostgreSQL (SQL préparé avec Claude chat, exécuté et vérifié par Rémy)
  - [x] Étapes 0 et 1 : `tp-db/docker-compose.yml` (`postgres:16`), `sql/init/01-schema.sql`
  - [x] Étape 2 : `02-seed.sql`, 5 insertions refusées, suppression de Bob avec et sans cascade
  - [x] Étape 3 : `sql/requetes.sql`, 8 requêtes avec résultats
  - [x] Étape 4 : transactions (isolation et atomicité)
  - [x] Étape 5 : index, `MESURES.md`
  - [x] Étape 6 : `03-schema-v2.sql`, `tests-contraintes.sql`, `REVIEW-schema.md`
- [ ] Séance 4 · Application en couches, Compose 3 services
  - [x] TP frontend, étape 1 : squelette et service Compose
  - [x] TP frontend, étape 2 : client d'API et gestionnaire d'erreurs
  - [x] TP frontend, étape 3 : liste et détail des objets
  - [x] TP frontend, étape 4 : création d'un objet avec formulaire et PRG
  - [x] TP frontend, étapes 5 et 6 : réservations, annulation, limites observées
  - [x] TP backend, étape 1 : configuration, engine SQLAlchemy et dépendance de session
  - [x] TP backend, étape 2 : modèles SQLAlchemy et relations
  - [x] TP backend, étape 3 : branchement d'Alembic et service PostgreSQL dans Compose
  - [x] TP backend, étape 3bis : piège du renommage (`docs/review-migrations.md`)
  - [x] TP backend, étape 4 : verticale `items` en couches, propriétaire vérifié par le service
  - [x] TP backend, tests : base `gearshare_test`, 53 tests verts
  - [x] TP backend, étape 5 : N+1 mesuré (22 requêtes) et corrigé avec `selectinload` (2 requêtes)
  - [ ] TP backend, étape 6 : Compose à trois services et migrations au démarrage
  - [ ] TP backend, étape 7 : verticale `reservations`
- [ ] Séance 5 · Authentification JWT
- [ ] Séance 6 · Fondations agentic (pas encore publié)
- [ ] Séance 7 · Flow complet d'une feature (pas encore publié)

## Rendu final

- [ ] Au moins une fonctionnalité en plus, implémentée avec un agent et documentée
- [ ] Dossier `docs/` complet (fonctionnalités, traces, choix d'architecture)
- [ ] `docs/retour-experience.md` (difficultés, pistes d'amélioration)
- [ ] Lancement en une commande vérifié sur un clone propre
- [ ] Lien du dépôt envoyé à l'enseignant

## Décisions

- 2026-09-23 : dépôt organisé en `backend/` + `docs/`, frontend ajouté en séance 4.
- 2026-09-23 : Rémy fait les commits lui-même après relecture du diff.
- 2026-09-24 : `PUT /items/{item_id}` réutilise `ItemCreate` plutôt qu'un schéma dédié,
  puisque le contrat d'un remplacement complet est celui d'une création.
- 2026-09-24 : stockage `FAKE_DB` en mémoire, un par router, provisoire jusqu'à la séance 3.
- 2026-09-24 : pas de `skip` sur `GET /reservations` ni de schéma `ReservationUpdate`, écarts assumés avec le gabarit d'`items`, notés dans `REVIEW.md`.
- 2026-09-26 : `_next_id()` vaut `max(FAKE_DB) + 1` ; supprimer l'id le plus grand le libère pour le `POST` suivant.
- 2026-09-26 : `tests/` et `pytest.ini` copiés dans l'image et montés en volume.
- 2026-09-26 : un test par `raise`, pas de test sur `/items/abc` (conversion FastAPI) ; erreur de dates testée par `loc == ["body"]` et `"date_fin" in msg`.
- 2026-09-26 (Rémy) : si la notification échoue, l'annulation reste acquise (200) ; on attrape `(ConnectionError, TimeoutError)`.
- 2026-09-30 (Rémy) : l'agent ne crée ni ne modifie aucun fichier de `tp-db/` ; suivi seulement, image `postgres:16`.
- 2026-10-22 (Rémy) : exception pour l'étape 6 de la séance 3, le DDL de `03-schema-v2.sql` est écrit
  par GitHub Copilot (mode Agent), puis relu et testé par Rémy (`tp-db/REVIEW-schema.md`).
- 2026-09-30 (Rémy) : un compte supprimé sera désactivé et anonymisé plutôt qu'effacé, pour garder l'historique.
- 2026-10-22 : ajout de `ReservationUpdate` et de `PATCH /reservations/{reservation_id}`, contrat imposé par le TP frontend de la séance 4. Seul `{"statut": "annulee"}` est accepté. La logique est partagée avec `POST /reservations/{reservation_id}/annuler`, gardé pour que les tests de la séance 2 passent sans modification.
- 2026-10-22 : le frontend appelle `GET /reservations`, `POST /reservations` et `PATCH /reservations/{reservation_id}` ; la page de détail permet de réserver et d'annuler avec PRG.
- 2026-10-27 : Alembic lit `settings.database_url`, utilise `Base.metadata` avec tous les modèles importés, et le service backend attend PostgreSQL sain dans Compose ; les migrations restent manuelles jusqu'à l'étape 6.
- 2026-10-27 : les exceptions métier sont traduites en HTTP par un gestionnaire global dans `main.py` ; les repositories ne font jamais de `commit()`, la transaction reste gérée par `get_db`.
- 2026-10-27 : `ItemService` vérifie l'existence de `owner_id` avec `UserRepository` avant création, remplacement ou modification du propriétaire.
- 2026-10-27 : les tests utilisent `TEST_DATABASE_URL`, un schéma créé par `Base.metadata`, une transaction annulée par test et l'override de `get_db`. Les réservations restent en mémoire jusqu'à l'étape 7.
- 2026-10-27 : `OwnerRead` expose seulement `id` et `display_name` dans `ItemRead`, construit depuis la relation SQLAlchemy `Item.owner`. La requête de liste reste inchangée pour permettre la mesure du N+1.
- 2026-10-27 (Rémy) : `ItemRepository.list` charge les propriétaires avec `selectinload(Item.owner)`,
  ce qui ramène `GET /items` de 22 à 2 requêtes.

## Questions ouvertes

- `POST /reservations` accepte un `item_id` inexistant (201) et deux réservations actives sur le même créneau. Réglé à l'étape 7 du TP 2 (verticale `reservations` en couches).
- Binôme ou seul : à préciser. Date de rendu : à confirmer (synthèse annoncée par l'enseignant).
