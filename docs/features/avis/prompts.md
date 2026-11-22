# Prompts, feature avis

Prompts donnés à GitHub Copilot (mode Agent), copiés tels quels. Réponses préparées avec l'aide
de Claude.

## Étape 3 : fiche feature, avec le skill fiche-feature

```text
/fiche-feature Nouvelle feature « avis », à ranger dans docs/features/avis/. Voici l'intuition de départ, telle qu'elle nous arrive :

« Lors d'une enquête auprès des utilisateurs de GearShare, six utilisateurs sur dix disent hésiter à emprunter du matériel à quelqu'un qu'ils ne connaissent pas. Plusieurs prêteurs regrettent de ne pas pouvoir se faire une réputation. »
```

Le skill a posé ses questions par séries (problème, qui donne et reçoit un avis, à quel moment,
cas de refus, hors périmètre), puis 4 questions à choix. Mes choix : commentaire optionnel,
moyenne et nombre d'avis seulement, une décimale avec « Aucun avis » quand il n'y en a pas,
métrique principale = part des réservations chez un prêteur inconnu de l'emprunteur.
