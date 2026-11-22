# Revue de la feature avis

Décisions et vérifications faites par moi. Texte mis en forme avec l'aide de Claude.

## 1. Revue par le relecteur (étape 6 du TP)

Conversation neuve, mode Plan de Copilot avec `.github/agents/relecteur.agent.md` comme consignes
(ma version de VS Code n'affiche pas les agents personnalisés dans le chat). 8 défauts remontés.

| Défaut remonté | Décision | Raison |
|---|---|---|
| `frontend/app/routers/reservations.py:74` : 401 non géré à la clôture | Écarté | Faux positif. Le 401 n'est pas dans la liste attrapée par la route, il est relancé et traité par le gestionnaire global de `frontend/app/main.py` (séance 5), qui redirige vers `/connexion`. Vérifié : POST sans cookie, réponse 303 vers `/connexion?suivant=...`. |
| `frontend/app/routers/reservations.py:90` : 401 non géré à l'avis | Écarté | Même raison, même vérification. |
| `.github/copilot-instructions.md`, `CLAUDE.md`, `AGENTS.md` hors périmètre | Écarté | Livrables des étapes 0 à 2 du TP, que le prof demande de faire sur la branche `feature/avis`. Remarque juste sur le principe : dans une équipe, l'outillage aurait sa propre PR. |
| `docs/templates/*` hors périmètre | Écarté | Étape 1 du TP, même raison. |
| `docs/tp/seance-6/prompts.md` hors périmètre | Écarté | Trace de l'étape 0, même raison. |

Le relecteur n'a rien trouvé sur l'API, la base, les couches et la sécurité.

## 2. Ma revue étape par étape

Les défauts que j'ai trouvés en relisant chaque diff, avant le relecteur :

| Étape du plan | Défaut | Correction |
|---|---|---|
| Plan | Prérequis (clôture) en étape 2, commandes `pytest backend/tests/...` fausses dans le conteneur, `list.html` hors MVP, pas de `ON DELETE CASCADE`, frontend dépendant d'une donnée jamais fournie | 10 remarques renvoyées au planificateur |
| 1. Clôture | Condition `item is None` impossible (clé étrangère) qui aurait masqué une erreur en 403 | Remplacée par `reservation.item.owner_id` |
| 2. Modèle et migration | `created_at` nullable et sans valeur par défaut, toujours `NULL` | Migration locale annulée, corrigée, réappliquée |
| 2. Modèle et migration | `tests/test_avis.py` absent de la liste de l'étape | Oubli du plan, l'agent a demandé avant de créer le fichier |
| 3. Avis | Double `getattr` sur `exc.orig.diag`, déjà corrigé une fois dans le projet | Simplifié, convention ajoutée à `AGENTS.md` |
| 3. Avis | Aucun test ne protégeait la traduction de `IntegrityError` | Test de course ajouté |
| 4. Réputation | `routers/items.py` modifié hors plan sans demander, `setattr` sur l'objet SQLAlchemy, dépendance optionnelle avec repli caché, `selectinload` inutile | 4 remarques renvoyées à l'agent |
| 6. Recette | 3 imports mal triés, lint jamais lancé par l'agent malgré `AGENTS.md` | `ruff check --fix` |

## 3. Mutations

Chaque règle cassée volontairement, puis restaurée :

| Règle cassée | Test qui passe au rouge |
|---|---|
| Vérification du propriétaire à la clôture | `test_ac_01_3_cloture_par_un_non_proprietaire_renvoie_403` |
| Contrainte `UNIQUE` sur la réservation | `test_ac_02_8_base_refuse_un_second_avis_par_reservation` |
| Vérification de l'emprunteur | `test_ac_02_6_publie_sur_reservation_d_un_autre_emprunteur_renvoie_403` |
| Traduction de `IntegrityError` en 409 | `test_ac_02_8_course_simulee_renvoie_409` |
| Filtre sur le propriétaire dans la moyenne | `test_ac_03_3_moyenne_calculee_sur_tous_les_avis_du_preteur` |

## 4. Recette

- Un test au moins pour chacun des 18 critères, 150 tests verts, lint propre.
- Navigateur : « Aucun avis » en visiteur, clôture par le prêteur, avis publié par l'emprunteur,
  « 4.0/5 (1 avis) », second avis refusé avec un message, réputation visible sans connexion.
