---
description: Reprendre le travail là où on s'est arrêté
---
Lis `docs/suivi/SUIVI.md` et les deux dernières entrées de `docs/suivi/journal.md`.
Vérifie l'état réel du dépôt avec `git status` et `git log --oneline -5`.
Vérifie si le support de cours a changé : `git -C ../cours fetch -q` puis
`git -C ../cours log --oneline HEAD..origin/main`. S'il y a du nouveau, dis-le et propose
`git -C ../cours pull`.

Puis résume en 5 lignes maximum : où on en est, ce qui reste, et la prochaine étape proposée.
Ne modifie aucun fichier.
