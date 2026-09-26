# Suivi du projet

Dernière mise à jour : 2026-09-26

## En cours

TP séance 2, étape 4 faite (notification d'annulation mockée, 48 tests verts,
couverture 100 %), en attente de relecture et de commit par Rémy.
Reste aussi la dernière section de `docs/tp/seance-1/REVIEW.md` : « Ce que je retiens du
travail avec l'agent ».

## Prochaine étape

Séance 2 : vérifier dans `../cours/seances/seance-2-tests/tp/` s'il reste des étapes
(sections 7 et 8 du cours : couverture, tests qui ne testent rien).

## Avancement des séances

- [ ] Séance 0 · Docker (optionnelle)
- [x] Séance 1 · API FastAPI
  - [x] Projet initialisé à partir du `projet-demo`
  - [x] Étapes 1 à 4 : path/query params, schémas, CRUD `items`
  - [x] Étape 5 : découpage en routers
  - [x] Étape 6 : `reservations` générée par agent, `SPEC-reservations.md`, `REVIEW.md`
- [ ] Séance 2 · Tests pytest
  - [x] Étape 1 : pytest dans le conteneur, `test_health.py`, compteurs globaux supprimés
  - [x] Étape 2 : `conftest.py` (`Storage`, `storage`, `client`, `item_velo`), `test_items.py`
  - [x] Étape 3 : `reservation_active`, `test_reservations.py`, `test_schemas.py`
  - [x] Étape 4 : notification d'annulation, tests avec `monkeypatch` et `Mock`
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
- 2026-09-26 : tests en plus de la grille demandée : validations `PATCH`, query et path.
  Pas de test sur `/items/abc` (conversion faite par FastAPI). Un test par 404 plutôt qu'un
  `parametrize` sur la méthode, pour qu'un `raise` corresponde à un test nommé.
- 2026-09-26 : erreur de dates testée par `loc == ["body"]` et `"date_fin" in msg`, car le
  `model_validator` rattache l'erreur au corps entier et non à un champ.
- 2026-09-26 (décision de Rémy) : si la notification d'annulation échoue, l'annulation reste
  acquise et la route renvoie 200. On attrape `(ConnectionError, TimeoutError)`, pas
  `Exception` : un délai dépassé ne doit pas donner un 500 alors que l'annulation est faite.
  L'échec est journalisé en `warning`, sans détail pour le client.

## Questions ouvertes

- `POST /reservations` accepte un `item_id` qui n'existe pas (201). Hors spec, non testé.
  À revoir en séance 4 avec les clés étrangères.
- Binôme ou seul : à préciser.
- Date de rendu : à confirmer (document de synthèse annoncé par l'enseignant).
- Pas encore de `.env.example` à la racine, alors que le lancement en une commande est
  un critère bloquant du rendu. À traiter au plus tard en séance 4.
