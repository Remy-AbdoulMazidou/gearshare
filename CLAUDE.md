# GearShare : instructions projet

Projet du module « Fullstack data application » (ESIEE Paris, E5 DSIA). Plateforme de prêt de
matériel entre étudiants : publier du matériel, chercher, réserver un créneau, gérer son compte,
historique de prêts, avis. Étudiant : Rémy. Tout se fait en français.

## Mémoire du projet

État actuel du projet (à lire avant toute action) :

@docs/suivi/SUIVI.md

Historique détaillé des sessions : `docs/suivi/journal.md` (à consulter seulement si besoin).

## Support de cours

Le dépôt de l'enseignant est cloné en lecture seule dans `../cours/`. Ne jamais le modifier.
Avant une tâche liée à une séance, lire `../cours/seances/<séance>/cours/README.md` et
`../cours/seances/<séance>/tp/README.md`, et suivre ce qu'ils demandent. Le sujet et la grille
d'évaluation seront publiés plus tard dans ce dépôt.

## Stack imposée

- Backend : Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic
- Base : PostgreSQL 17
- Frontend : application Python séparée, qui passe uniquement par l'API REST
- Docker Compose, au moins 3 services (frontend, backend, base) à partir de la séance 4
- Auth : utilisateurs, JWT, mots de passe hachés
- Tests : pytest, cas nominaux et cas d'erreur

Critère bloquant du rendu : `git clone`, `cp .env.example .env`, `docker compose up`, et tout
marche sans intervention.

## Architecture

```text
backend/app/
  main.py         création de l'app, include_router
  routers/        HTTP entrant et sortant uniquement
  schemas/        modèles Pydantic (contrat public)
  services/       logique métier
  repositories/   accès aux données
  models/         modèles SQLAlchemy
backend/tests/
```

Les routers n'accèdent jamais directement aux données : ils passent par les services.

## Conventions de code

- Pour chaque ressource, trois schémas : `XxxCreate`, `XxxUpdate` (tous les champs optionnels),
  `XxxRead` (jamais de secret). `model_config = ConfigDict(extra="forbid")` sur les entrées.
- `response_model` sur chaque route.
- Codes HTTP exacts : 201 à la création, 204 à la suppression (sans corps), 404, 409, 422.
  Aucun 500 volontaire. Pas de détail technique dans les messages d'erreur.
- Contraintes de validation dans Pydantic (`Field`, `model_validator`), pas en `if` dans le router.
- PATCH : `model_dump(exclude_unset=True)`.
- Routes littérales déclarées avant les routes paramétrées.
- `def` par défaut. `async def` seulement s'il y a un `await` dedans.
- Pagination toujours plafonnée (`limit` au maximum 100).
- Dépendances épinglées dans `requirements.txt`. Aucune nouvelle dépendance sans le justifier.

## Tests

- `TestClient`, fixtures dans `tests/conftest.py`, scope `function`.
- Avant PostgreSQL : dataclass `Storage` qui référence les dictionnaires des routers,
  fixture `storage`, et `client` qui dépend de `storage` (pas d'`autouse`).
- Noms de tests en français et explicites. Given / When / Then quand ce n'est pas évident.
- `parametrize` pour les cas de validation, en vérifiant le champ en erreur (`loc[-1]`).
- Pour chaque `raise` d'un router ou d'un service, un test.
- Ne jamais mocker le sujet du test ni le stockage. Mocker l'horloge et les services externes.
- Couverture visée : 70 à 80 %.
- Lancer les tests : `docker compose run --rm api pytest` (depuis `backend/`).

## Façon de travailler

1. Avant de coder, proposer un plan court (fichiers touchés, étapes) et attendre la validation.
2. Avancer par petites étapes. Après chaque étape, vérifier : tests verts, API qui démarre.
3. Ne jamais lancer `git commit` ni `git push`. Rémy relit le diff et commite lui-même.
   Proposer un message de commit court, en français, sans préfixe.
4. Garder un code sobre, au niveau du cours. Pas d'abstraction ni de fonctionnalité non demandée.
5. À la fin de chaque étape, donner une section « À savoir expliquer » : 3 à 5 points du code
   produit que Rémy doit pouvoir justifier à l'oral.
6. Jamais de secret dans le code. Configuration par variables d'environnement, `.env` ignoré,
   `.env.example` versionné.

## Documentation et traces (évaluées)

- Livrables des TP : `docs/tp/seance-N/`.
- Chaque fonctionnalité ajoutée : `docs/features/NN-nom/` avec
  `presentation.md` (parcours utilisateur, critères d'acceptation), `plan.md`,
  `prompts.md` (prompts réellement utilisés, copiés tels quels) et `review.md`.
- Un document rédigé par l'agent le dit en première ligne :
  « Rédigé avec Claude Code, relu et corrigé par Rémy. »
- Les fichiers de review (`REVIEW.md`, `review.md`) et `docs/retour-experience.md` sont écrits
  par Rémy. L'agent peut proposer une trame ou des questions, jamais le contenu.
- Style des docs : français simple, phrases courtes, pas de formules marketing, pas d'emojis.

## Mise à jour de la mémoire (obligatoire)

À la fin de chaque tâche terminée, et quand Rémy tape `/cloturer` :

1. Mettre à jour `docs/suivi/SUIVI.md` : cocher ce qui est fait, mettre à jour « En cours »,
   « Prochaine étape » et « Décisions ». Ce fichier reste court (moins de 80 lignes).
2. Ajouter une entrée à la fin de `docs/suivi/journal.md` : date, ce qui a été fait,
   par qui (Rémy ou Claude Code), problèmes rencontrés, corrections apportées par Rémy.
