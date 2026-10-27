# Suivi du projet

Dernière mise à jour : 2026-10-27

## En cours

TP 2 de la séance 4, étape 2 terminée : modèles SQLAlchemy correspondant au schéma SQL initial.

## Prochaine étape

TP 2 de la séance 4 : brancher le backend sur PostgreSQL (SQLAlchemy, Alembic) sans modifier le frontend.

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
- [ ] Séance 5 · Authentification JWT (pas encore publié)
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
- 2026-09-30 (Rémy) : un compte supprimé sera désactivé et anonymisé plutôt qu'effacé, pour garder l'historique.
- 2026-10-22 : ajout de `ReservationUpdate` et de `PATCH /reservations/{reservation_id}`, contrat imposé par le TP frontend de la séance 4. Seul `{"statut": "annulee"}` est accepté. La logique est partagée avec `POST /reservations/{reservation_id}/annuler`, gardé pour que les tests de la séance 2 passent sans modification.
- 2026-10-22 : le frontend appelle `GET /reservations`, `POST /reservations` et `PATCH /reservations/{reservation_id}` ; la page de détail permet de réserver et d'annuler avec PRG.

## Questions ouvertes

- `POST /reservations` accepte un `item_id` inexistant (201) et deux réservations actives sur le même créneau. Hors spec, non testé, noté dans `REVIEW.md`.
- Binôme ou seul : à préciser. Date de rendu : à confirmer (synthèse annoncée par l'enseignant).
- Pas encore de `.env.example` à la racine, alors que le lancement en une commande est un critère bloquant du rendu. À traiter au plus tard en séance 4.
