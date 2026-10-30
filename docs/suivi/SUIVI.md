# Suivi du projet

Dernière mise à jour : 2026-10-30

## En cours

Séance 5 terminée (100 tests). Fonctionnalité 01 : la contrainte `EXCLUDE` des réservations est
dans une migration Alembic, l'API répond 409 en cas de course, 104 tests verts.

## Prochaine étape

Séance 6 : fondations agentic (support à venir). En attendant : attaque temporelle sur le login,
fiches des fonctionnalités 02 et 03, `docs/retour-experience.md`.

## Avancement des séances

- [ ] Séance 0 · Docker (optionnelle)
- [x] Séance 1 · API FastAPI : CRUD `items`, `reservations` générée par agent, `REVIEW.md`, review Copilot
- [x] Séance 2 · Tests pytest : 48 tests, notification mockée, mutations (`MUTATIONS.md`)
- [x] Séance 3 · PostgreSQL : schéma, requêtes, transactions, `MESURES.md`, schéma v2 et
  `REVIEW-schema.md` (SQL préparé avec Claude chat, exécuté et vérifié par Rémy)
- [x] Séance 4 · Application en couches, Compose 3 services
  - [x] TP 1 frontend : liste, détail, création, réservation et annulation (PRG, 422, 409)
  - [x] TP 2 backend : couches `items` et `reservations` sur PostgreSQL, Alembic, piège du renommage,
    N+1 (22 → 2 requêtes), service `migrate`, 62 tests sur `gearshare_test`, docs de review
- [x] Séance 5 · Authentification JWT
  - [x] Étape 0 : dépendances, `JWT_SECRET` et `COOKIE_SECURE`
  - [x] Étape 1 : hachage des mots de passe
  - [x] Étape 2 : inscription
  - [x] Étape 3 : connexion et émission d'un JWT
  - [x] Étape 4 : `get_current_user`, `/auth/me` et routes protégées
  - [x] Étape 5 : propriété des items et annulation des réservations en 403
  - [x] Étape 6 : matrice de tests d'authentification
  - [x] Étape 7 : connexion, inscription, déconnexion et transmission du JWT côté frontend
  - [x] Étapes 8 et 9 : failles exploitées (secret faible, expiration, compte supprimé), relecture finale
- [ ] Séances 6 et 7 · Fondations agentic, flow complet d'une feature (pas encore publiées)

## Rendu final

- [ ] Au moins une fonctionnalité en plus, implémentée avec un agent et documentée
- [ ] Dossier `docs/` complet (fonctionnalités, traces, choix d'architecture)
- [ ] `docs/retour-experience.md` (difficultés, pistes d'amélioration)
- [ ] Lancement en une commande vérifié sur un clone propre
- [ ] Lien du dépôt envoyé à l'enseignant

## Décisions

- 2026-09-23 à 2026-09-30 : dépôt en `backend/` + `docs/`, frontend ajouté en séance 4,
  commits faits par Rémy. Stockage mémoire et `tp-db/` provisoires jusqu'à PostgreSQL.
- 2026-09-24 à 2026-09-26 : `PUT` réutilise `ItemCreate`, pas de `skip` sur les réservations,
  validation par `loc[-1]`, notification d'annulation tolérante à `ConnectionError` et `TimeoutError`.
- 2026-10-22 : DDL v2 préparé par GitHub Copilot (mode Agent), relu et testé par Rémy.
  `PATCH` d'annulation ajouté au frontend, avec l'ancienne route conservée pour les tests.
- 2026-10-27 : Alembic lit la configuration, les repositories ne font pas de `commit`, et
  les tests utilisent `gearshare_test` avec une transaction annulée par test.
- 2026-10-27 : `OwnerRead` et `selectinload(Item.owner)` font passer `GET /items` de 22 à 2 requêtes.
- 2026-10-30 : migrations via un service Compose `migrate`. Inscription et connexion JWT en couches.
- 2026-10-30 : `get_current_user` utilise `OAuth2PasswordBearer`, relit l'utilisateur par
  `UserRepository` et uniformise les erreurs d'authentification en 401 avec `Bearer`.
- 2026-10-30 : `owner_id` et `borrower_id` viennent du jeton. `ItemService` vérifie la propriété
  avant PUT, PATCH et DELETE. `ReservationService` autorise l'annulation à l'emprunteur ou au
  propriétaire de l'item, dans l'ordre 404, 403, 409.
- 2026-10-30 : les fixtures `client_alice` et `client_bob` utilisent des instances distinctes
  de `TestClient`. La matrice couvre les accès anonymes, propriétaires et autres utilisateurs.
- 2026-10-30 : le frontend lit le JWT dans le cookie `access_token`, le transmet en paramètre à
  `ApiClient`, et redirige les `401` vers `/connexion` sans stocker le jeton dans le client partagé.
- 2026-10-30 : contrainte `EXCLUDE` des réservations ajoutée par une migration écrite à la main
  (autogenerate ne la détecte pas). Le service garde sa vérification, la base est le dernier
  garde-fou et l'API répond 409 en cas de course (`docs/features/01-pas-de-double-reservation/`).

## Questions ouvertes

- Binôme ou seul : à préciser. Date de rendu : à confirmer (synthèse annoncée par l'enseignant).
