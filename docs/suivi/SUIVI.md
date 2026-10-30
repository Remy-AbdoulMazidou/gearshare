# Suivi du projet

Dernière mise à jour : 2026-10-30

## En cours

TP 2 de la séance 4, étapes 0 à 7 terminées : backend en couches pour `items` et
`reservations` sur PostgreSQL, tests sur `gearshare_test` (62 tests verts), N+1 corrigé,
service `migrate` (`docs/choix-migrations.md`), frontend branché sur la vraie base.

## Prochaine étape

Relecture documentaire de la verticale `reservations` (`docs/review-couches.md` et
`docs/cas-tests-chevauchement.md`).

## Avancement des séances

- [ ] Séance 0 · Docker (optionnelle)
- [x] Séance 1 · API FastAPI : CRUD `items`, `reservations` générée par agent, `REVIEW.md`, review Copilot
- [x] Séance 2 · Tests pytest : 48 tests, notification mockée, mutations (`MUTATIONS.md`)
- [x] Séance 3 · PostgreSQL : schéma, requêtes, transactions, `MESURES.md`, schéma v2 et
  `REVIEW-schema.md` (SQL préparé avec Claude chat, exécuté et vérifié par Rémy)
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
  - [x] TP backend, étape 6 : service `migrate`, vérification depuis zéro, frontend sur la vraie base
  - [x] TP backend, étape 7 : verticale `reservations`
- [ ] Séance 5 · Authentification JWT
- [ ] Séances 6 et 7 · Fondations agentic, flow complet d'une feature (pas encore publiées)

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
- 2026-09-26 : un test par `raise`, pas de test sur `/items/abc` (conversion FastAPI) ; erreur de dates testée par `loc == ["body"]` et `"date_fin" in msg`.
- 2026-09-26 (Rémy) : si la notification échoue, l'annulation reste acquise (200) ; on attrape `(ConnectionError, TimeoutError)`.
- 2026-09-30 (Rémy) : l'agent ne crée ni ne modifie aucun fichier de `tp-db/` ; suivi seulement, image `postgres:16`.
- 2026-09-30 (Rémy) : un compte supprimé sera désactivé et anonymisé plutôt qu'effacé, pour garder l'historique.
- 2026-10-22 (Rémy) : exception pour l'étape 6 de la séance 3, le DDL de `03-schema-v2.sql` est écrit
  par GitHub Copilot (mode Agent), puis relu et testé par Rémy (`tp-db/REVIEW-schema.md`).
- 2026-10-22 : `PATCH /reservations/{reservation_id}` (seul `{"statut": "annulee"}` accepté) ajouté pour
  le frontend, `POST .../annuler` gardé pour les tests de la séance 2, logique partagée.
- 2026-10-27 : Alembic lit `settings.database_url` ; migrations manuelles jusqu'à l'étape 6.
- 2026-10-27 : gestionnaire global des exceptions métier dans `main.py` ; aucun `commit()` dans les
  repositories, la transaction est gérée par `get_db`.
- 2026-10-27 : `ItemService` vérifie le propriétaire avec `UserRepository` (404 au lieu d'un 500).
- 2026-10-27 : tests sur `gearshare_test`, une transaction annulée par test ; réservations en mémoire
  jusqu'à l'étape 7.
- 2026-10-27 (Rémy) : `OwnerRead` (`id`, `display_name`) dans `ItemRead`, chargé avec
  `selectinload(Item.owner)` : `GET /items` passe de 22 à 2 requêtes.
- 2026-10-30 : choix de l'option 2 pour les migrations : service Compose `migrate` dédié, attendu
  par le backend après la disponibilité de PostgreSQL.
- 2026-10-30 : la verticale `reservations` utilise `borrower_id` jusqu'à l'authentification,
  vérifie l'item, l'emprunteur, la disponibilité et les chevauchements dans le service.

## Questions ouvertes

- `owner_id` fixé à 1 (utilisateur de démo) dans le frontend, `# TODO séance 5` : remplacé par
  l'utilisateur connecté en séance 5.
- Le frontend de réservation devra afficher les conflits 409 à l'étape de relecture du TP 2.
- Binôme ou seul : à préciser. Date de rendu : à confirmer (synthèse annoncée par l'enseignant).
