# Suivi du projet

Dernière mise à jour : 2026-09-26

## En cours

TP séance 2, étape 1 faite (pytest dans le conteneur, `_next_id()` calculé depuis `FAKE_DB`),
en attente de relecture et de commit par Rémy.
Reste aussi la dernière section de `docs/tp/seance-1/REVIEW.md` : « Ce que je retiens du
travail avec l'agent ».

## Prochaine étape

Séance 2, suite : `tests/conftest.py` avec `Storage`, fixtures `storage` et `client`
(cours section 3.4), puis tests de `items` et `reservations`.

## Avancement des séances

- [ ] Séance 0 · Docker (optionnelle)
- [x] Séance 1 · API FastAPI
  - [x] Projet initialisé à partir du `projet-demo`
  - [x] Étapes 1 à 4 : path/query params, schémas, CRUD `items`
  - [x] Étape 5 : découpage en routers
  - [x] Étape 6 : `reservations` générée par agent, `SPEC-reservations.md`, `REVIEW.md`
- [ ] Séance 2 · Tests pytest
  - [x] Étape 1 : pytest dans le conteneur, `test_health.py`, compteurs globaux supprimés
- [ ] Séance 3 · PostgreSQL (support pas encore publié)
- [ ] Séance 4 · Application en couches, Compose 3 services (pas encore publié)
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
- 2026-09-24 : pas de schéma `ReservationUpdate` ni de `skip` sur `GET /reservations`,
  la spec ne les prévoit pas. Écarts assumés avec le gabarit d'`items`, notés dans `REVIEW.md`.
- 2026-09-26 : `_next_id()` vaut `max(FAKE_DB) + 1`. Changement de comportement assumé :
  supprimer l'item d'id le plus grand libère son id, réattribué au `POST` suivant
  (1, 2, 3, suppression du 3, le prochain vaut 3 et non plus 4). Disparaît en séance 3.
- 2026-09-26 : `tests/` et `pytest.ini` copiés dans l'image et montés en volume.
  On garde `dict[int, dict]` pour `FAKE_DB`.

## Questions ouvertes

- Binôme ou seul : à préciser.
- Date de rendu : à confirmer (document de synthèse annoncé par l'enseignant).
- Pas encore de `.env.example` à la racine, alors que le lancement en une commande est
  un critère bloquant du rendu. À traiter au plus tard en séance 4.
