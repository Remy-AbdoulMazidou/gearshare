# Suivi du projet

Dernière mise à jour : 2026-10-30

## En cours

Étapes 1 à 3 de la séance 5 terminées : hachage PBKDF2-HMAC-SHA256, inscription et connexion JWT.
TP 2 de la séance 4, étapes 0 à 7 terminées : backend en couches pour `items` et
`reservations` sur PostgreSQL, tests sur `gearshare_test` (66 tests verts), N+1 corrigé,
service `migrate` (`docs/choix-migrations.md`), frontend branché sur la vraie base.

## Prochaine étape

Séance 5, étape 4 : dépendance `get_current_user` et protection des routes. `owner_id` et
`borrower_id` fixés à 1 dans le frontend disparaîtront.

## Avancement des séances

- [ ] Séance 0 · Docker (optionnelle)
- [x] Séance 1 · API FastAPI : CRUD `items`, `reservations` générée par agent, `REVIEW.md`, review Copilot
- [x] Séance 2 · Tests pytest : 48 tests, notification mockée, mutations (`MUTATIONS.md`)
- [x] Séance 3 · PostgreSQL : schéma, requêtes, transactions, `MESURES.md`, schéma v2 et
  `REVIEW-schema.md` (SQL préparé avec Claude chat, exécuté et vérifié par Rémy)
- [x] Séance 4 · Application en couches, Compose 3 services
  - [x] TP 1 frontend : liste, détail, création, réservation et annulation (PRG, 422, 409)
  - [x] TP 2 backend : couches `items` et `reservations` sur PostgreSQL, Alembic, piège du renommage,
    N+1 (22 → 2 requêtes), service `migrate`, 66 tests sur `gearshare_test`, docs de review
- [ ] Séance 5 · Authentification JWT
  - [x] Étape 1 : hachage des mots de passe
  - [x] Étape 2 : inscription
  - [x] Étape 3 : connexion et émission d'un JWT
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
- 2026-10-27 : tests sur `gearshare_test`, une transaction annulée par test.
- 2026-10-30 (Rémy) : service `migrate` pour appliquer les migrations au démarrage
  (`docs/choix-migrations.md`). Deux réservations jointives ne sont pas en conflit.
- 2026-10-27 (Rémy) : `OwnerRead` (`id`, `display_name`) dans `ItemRead`, chargé avec
  `selectinload(Item.owner)` : `GET /items` passe de 22 à 2 requêtes.
- 2026-10-30 : choix de l'option 2 pour les migrations : service Compose `migrate` dédié, attendu
  par le backend après la disponibilité de PostgreSQL.
- 2026-10-30 : l'inscription vérifie l'email dans `AuthService`, hache le mot de passe avec
  PBKDF2 avant ajout, et renvoie `409` pour un email déjà utilisé.
- 2026-10-30 : `POST /auth/login` vérifie les identifiants avec un message identique en cas
  d'email inconnu ou de mauvais mot de passe, et émet un JWT HS256 limité à `sub`, `iat` et `exp`.
- 2026-10-30 : la verticale `reservations` utilise `borrower_id` jusqu'à l'authentification,
  vérifie l'item, l'emprunteur, la disponibilité et les chevauchements dans le service.

## Questions ouvertes

- `owner_id` et `borrower_id` fixés à 1 (utilisateur de démo) dans le frontend, `# TODO séance 5`.
- Chevauchement vérifié par le service mais pas encore par la base : ajouter la contrainte
  `EXCLUDE` de la séance 3 dans une migration (`docs/review-couches.md`).
- Binôme ou seul : à préciser. Date de rendu : à confirmer (synthèse annoncée par l'enseignant).
