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
