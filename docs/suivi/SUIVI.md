# Suivi du projet

Dernière mise à jour : 2026-10-30

## En cours

Étapes 1 à 7 de la séance 5 terminées : hachage PBKDF2-HMAC-SHA256, inscription, connexion JWT,
protection des routes, vérification de propriété, matrice de tests d'autorisation et connexion
côté frontend.
TP 2 de la séance 4, étapes 0 à 7 terminées : backend en couches pour `items` et
`reservations` sur PostgreSQL, tests sur `gearshare_test` (66 tests verts), N+1 corrigé,
service `migrate` (`docs/choix-migrations.md`), frontend branché sur la vraie base.

## Prochaine étape

Séance 6 : fondations agentic (support à venir).

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
  - [x] Étape 4 : `get_current_user`, `/auth/me` et routes protégées
  - [x] Étape 5 : propriété des items et annulation des réservations en 403
  - [x] Étape 6 : matrice de tests d'authentification
  - [x] Étape 7 : connexion, inscription, déconnexion et transmission du JWT côté frontend
- [ ] Séances 6 et 7 · Fondations agentic, flow complet d'une feature (pas encore publiées)

## Rendu final

- [ ] Au moins une fonctionnalité en plus, implémentée avec un agent et documentée
- [ ] Dossier `docs/` complet (fonctionnalités, traces, choix d'architecture)
- [ ] `docs/retour-experience.md` (difficultés, pistes d'amélioration)
- [ ] Lancement en une commande vérifié sur un clone propre
- [ ] Lien du dépôt envoyé à l'enseignant

## Décisions

- 2026-09-23 à 2026-09-30 : dépôt en `backend/` + `docs/`, frontend ajouté en séance 4,
  commits faits par Rémy ; stockage mémoire et `tp-db/` provisoires jusqu'à PostgreSQL.
- 2026-09-24 à 2026-09-26 : `PUT` réutilise `ItemCreate`, pas de `skip` sur les réservations,
  validation par `loc[-1]`, notification d'annulation tolérante à `ConnectionError` et `TimeoutError`.
- 2026-10-22 : DDL v2 préparé par GitHub Copilot (mode Agent), relu et testé par Rémy ;
  `PATCH` d'annulation ajouté au frontend, avec l'ancienne route conservée pour les tests.
- 2026-10-27 : Alembic lit la configuration, les repositories ne font pas de `commit`, et
  les tests utilisent `gearshare_test` avec une transaction annulée par test.
- 2026-10-27 : `OwnerRead` et `selectinload(Item.owner)` font passer `GET /items` de 22 à 2 requêtes.
- 2026-10-30 : migrations via un service Compose `migrate` ; inscription et connexion JWT en couches.
- 2026-10-30 : `get_current_user` utilise `OAuth2PasswordBearer`, relit l'utilisateur par
  `UserRepository` et uniformise les erreurs d'authentification en 401 avec `Bearer`.
- 2026-10-30 : les identités `owner_id` et `borrower_id` des créations viennent du jeton ;
  les vérifications de propriété sont reportées à l'étape 5.
- 2026-10-30 : `ItemService` vérifie la propriété avant PUT, PATCH et DELETE ; `ReservationService`
  autorise l'annulation à l'emprunteur ou au propriétaire de l'item, dans l'ordre 404, 403, 409.
- 2026-10-30 : les fixtures `client_alice` et `client_bob` utilisent des instances distinctes
  de `TestClient` ; la matrice couvre les accès anonymes, propriétaires et autres utilisateurs.
- 2026-10-30 : le frontend lit le JWT dans le cookie `access_token`, le transmet en paramètre à
  `ApiClient`, et redirige les `401` vers `/connexion` sans stocker le jeton dans le client partagé.
- 2026-10-30 : `get_current_user` utilise `OAuth2PasswordBearer`, relit l'utilisateur par
  `UserRepository` et uniformise les erreurs d'authentification en 401 avec `Bearer`.
- 2026-10-30 : les identités `owner_id` et `borrower_id` des créations viennent du jeton ;
  les vérifications de propriété sont reportées à l'étape 5.

## Questions ouvertes

- Chevauchement vérifié par le service mais pas encore par la base : ajouter la contrainte
  `EXCLUDE` de la séance 3 dans une migration (`docs/review-couches.md`).
- Binôme ou seul : à préciser. Date de rendu : à confirmer (synthèse annoncée par l'enseignant).
