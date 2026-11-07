# Prompts utilisés pour la ressource reservations

Agent : Claude Code, en mode Plan.

## Prompt 1

Implémente la ressource décrite dans docs/tp/seance-1/SPEC-reservations.md.
Calque le style de backend/app/routers/items.py et branche le router dans main.py.
Respecte la spec à la lettre. Si un point est ambigu, pose-moi la question au lieu de choisir.
Propose d'abord ton plan.

## Questions posées par l'agent pendant le plan

- ReservationUpdate : la spec ne prévoit aucune modification, mais CLAUDE.md impose trois schémas par ressource.
  Mon choix : ne pas le créer, aucune route ne l'utiliserait.
- Pagination : la spec ne prévoit que limit sur GET /reservations, alors que GET /items a aussi skip.
  Mon choix : pas de skip, pour respecter la spec.

## Suite

Plan accepté en validant chaque fichier manuellement (schéma, router, main.py).

## Après la séance 5 : erreurs documentées dans OpenAPI

Contexte : ma REVIEW de la séance 1 (docs/tp/seance-1/REVIEW.md, « Limites connues ») note que les 404 et 409 n'apparaissent pas dans /docs. Aujourd'hui seuls le code de succès et le 422 sont documentés.

Objectif : chaque route documente dans OpenAPI les erreurs qu'elle peut vraiment renvoyer.

1. Crée backend/app/schemas/error.py avec un schéma ErreurRead (detail: str), qui correspond au corps renvoyé par le gestionnaire d'exceptions de main.py et par les HTTPException.

2. Dans backend/app/routers/items.py, reservations.py et auth.py, ajoute responses= sur chaque route, avec ErreurRead comme modèle et une description courte en français. Déduis les codes du code réel (services, get_current_user, gestionnaire d'exceptions), pas d'une supposition : 401 pour les routes qui demandent un jeton, 403 quand le service vérifie la propriété, 404 quand une ressource peut manquer, 409 pour les conflits. Ne documente pas le 422, FastAPI le fait déjà. Pour éviter la répétition, tu peux définir des dictionnaires de réponses communs dans le module schemas/error.py.

3. Avant de modifier, donne-moi le tableau route → codes d'erreur que tu comptes documenter, avec pour chaque code l'endroit du code qui le renvoie. Attends ma validation.

4. Après validation : ajoute dans backend/tests/test_openapi.py un test paramétré qui lit /openapi.json et vérifie la présence de ces codes pour chaque route. Lance docker compose exec backend pytest -q.

5. Ajoute ce prompt tel quel à la fin de docs/tp/seance-1/prompts.md sous le titre « Après la séance 5 : erreurs documentées dans OpenAPI » (crée la section si besoin).

Pas de commentaire inutile. Ne modifie pas docs/suivi/. Pas de commit.
