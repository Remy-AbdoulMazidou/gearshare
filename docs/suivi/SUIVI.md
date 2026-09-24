# Suivi du projet

Dernière mise à jour : 2026-09-24

## En cours

Rien pour l'instant.

## Prochaine étape

TP 1 (séance 1), étape 5 : déplacer les routes `items` dans `app/routers/items.py`.
Puis étape 6 : `reservations` générée par agent, `SPEC-reservations.md`, `REVIEW.md`.

## Avancement des séances

- [ ] Séance 0 · Docker (optionnelle)
- [ ] Séance 1 · API FastAPI
  - [x] Projet initialisé à partir du `projet-demo`
  - [x] Étapes 1 à 4 : path/query params, schémas, CRUD `items`
  - [ ] Étape 5 : découpage en routers
  - [ ] Étape 6 : `reservations` générée par agent, `SPEC-reservations.md`, `REVIEW.md`
- [ ] Séance 2 · Tests pytest
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
- 2026-09-24 : stockage `FAKE_DB` en mémoire dans `main.py`, provisoire jusqu'à la séance 3.

## Questions ouvertes

- Binôme ou seul : à préciser.
- Date de rendu : à confirmer (document de synthèse annoncé par l'enseignant).
- Pas encore de `.env.example` à la racine, alors que le lancement en une commande est
  un critère bloquant du rendu. À traiter au plus tard en séance 4.
