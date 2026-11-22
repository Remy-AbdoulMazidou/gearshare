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

## Étape 4 : plan d'implémentation

Ma version de VS Code n'affiche pas les agents personnalisés dans le chat. J'ai utilisé le mode
Plan de Copilot (qui ne modifie pas le code) avec le fichier du planificateur comme consignes.

```text
Joue le rôle de l'agent défini dans .github/agents/planificateur.agent.md et suis ses instructions à la lettre : tu ne modifies aucun fichier.

La fiche validée est docs/features/avis/fiche.md. Le modèle à remplir est docs/templates/plan-implementation.md. Respecte les conventions de AGENTS.md, notamment le nommage des tests test_ac_<story>_<critère>_... et la commande de test docker compose run --rm backend pytest.

Rends le plan complet dans ta réponse, en Markdown, prêt à être enregistré dans docs/features/avis/plan.md.
```

L'approbation du plan a échoué (fichier interne du mode Plan introuvable). Plan récupéré en mode
Interactive :

```text
Écris le plan que tu viens de proposer, tel quel et en entier, dans docs/features/avis/plan.md. Ne modifie aucun autre fichier et n'implémente rien.
```

Itération après ma relecture :

```text
Relecture du plan par Rémy. Corrige docs/features/avis/plan.md avec ces remarques, sans modifier aucun autre fichier, et laisse le statut à brouillon :

1. Le prérequis passe en premier : l'étape 1 devient la clôture d'une réservation, l'étape 2 le modèle Avis et sa migration. Mets à jour la colonne Étape du tableau de traçabilité.
2. Le conteneur backend travaille déjà dans backend/ : toutes les commandes de vérification utilisent tests/... et pas backend/tests/....
3. Retire frontend/app/templates/items/list.html de l'étape 5 : la réputation sur la liste est hors périmètre.
4. avis.reservation_id a ON DELETE CASCADE, car supprimer un objet supprime ses réservations en cascade. Ajoute ce point aux « À savoir expliquer » de l'étape du modèle.
5. Contraintes nommées : avis_reservation_uq (UNIQUE), avis_note_ck (note entre 1 et 5), avis_commentaire_ck (500 caractères au plus).
6. Le frontend ne masque pas le formulaire quand un avis existe déjà : l'API refuse le doublon et le message d'erreur s'affiche. Retire « masquer l'action si l'avis existe déjà ».
7. Tranche : nouveau fichier backend/app/routers/avis.py, route POST /reservations/{reservation_id}/avis, inclus dans main.py.
8. L'étape 6 devient « Recette finale » : grep -rn "test_ac_" backend/tests, suite complète docker compose run --rm backend pytest, lint, puis recette manuelle. Les tests restent écrits dans les étapes 1 à 4.
9. Noms de tests : corrige « aviss » en « avis » et retire l'accent de « entière ».
10. Remplace la ligne sous le titre par : « Rédigé avec GitHub Copilot (mode Plan) en suivant .github/agents/planificateur.agent.md, relu et corrigé par Rémy. »
```

## Implémentation, étape 1 du plan : clôture d'une réservation

```text
Implémente uniquement l'étape 1 de docs/features/avis/plan.md (clôture d'une réservation), en respectant AGENTS.md.

- Ne modifie que les fichiers listés dans cette étape. Si tu as besoin d'en toucher un autre, demande-moi avant.
- Écris les tests prévus par l'étape, avec exactement les noms du plan.
- Lance la vérification de l'étape, puis la suite complète : docker compose run --rm backend pytest -q.
- Ne modifie pas docs/suivi/. Pas de commit.
- Termine par les points « À savoir expliquer ».
```
