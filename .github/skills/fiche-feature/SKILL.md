---
name: fiche-feature
description: Rédige la fiche d'une nouvelle fonctionnalité de GearShare dans
  docs/features/<nom>/fiche.md. À utiliser quand on demande de cadrer, spécifier,
  décrire ou rédiger la PRD d'une feature, avant tout plan ou tout code.
---

# Rédiger une fiche feature

1. Ne rédige rien tout de suite. Pose d'abord des questions, une série à la fois, sur :
   le problème, les utilisateurs, les cas de refus, ce qui est hors périmètre.
2. Lis le code concerné (modèles, services, routers) pour remplir l'évaluation technique.
   Signale explicitement tout prérequis absent de l'existant.
3. Remplis docs/templates/fiche-feature.md et écris le résultat dans
   docs/features/<nom>/fiche.md.
4. Dans la section « Options et compromis », propose des options mais laisse la colonne
   « Décision » vide : c'est à moi de trancher.
5. Chaque user story a au moins un critère de refus (non connecté, pas le droit, ressource
   absente, doublon, donnée invalide).
6. Les critères d'acceptation décrivent un comportement observable de l'extérieur. Ils ne
   mentionnent ni route, ni code HTTP, ni nom de table.
7. Chaque critère porte un identifiant AC-<story>.<numéro>, repris tel quel dans les noms de
   tests (test_ac_<story>_<numéro>_...).
8. Laisse le statut à « brouillon ». C'est moi qui le passe à « validée ».
9. Ne crée ni ne modifie aucun autre fichier que la fiche.
