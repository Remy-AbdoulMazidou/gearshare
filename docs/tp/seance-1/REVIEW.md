# Review de la ressource reservations

Vérifications, tests et décisions faits par moi. Texte mis en forme avec l'aide de Claude.

Agent utilisé : Claude Code, en mode Plan, à partir de SPEC-reservations.md. J'ai validé chaque fichier à la main avant qu'il soit écrit.

| Point de contrôle | OK / KO | Comment je l'ai vérifié | Ce que j'ai corrigé |
|---|---|---|---|
| Les codes de statut correspondent à la spec (201, 404, 409) | OK | Bloc de tests curl : 201 à la création, 404 sur une réservation inexistante, 409 sur une double annulation. | Rien |
| `response_model` présent sur les 4 routes | OK | Lu dans le router au moment de valider le fichier, confirmé par le grep de l'agent (4 occurrences). | Rien |
| La validation `date_fin > date_debut` est dans le schéma Pydantic | OK | `model_validator(mode="after")` dans `schemas/reservation.py`. Testé avec des dates inversées et des dates égales : 422 dans les deux cas. | Rien |
| Le router n'accède pas au stockage de `items` | OK | Aucun import venant de `items`, le router a son propre `FAKE_DB`. Confirmé par le grep de l'agent. | Rien |
| Pas d'`async def` sans `await` | OK | Toutes les routes sont en `def`, vu dans le code et confirmé par le grep. | Rien |
| Aucune dépendance ajoutée dans `requirements.txt` | OK | `git status` : le fichier n'a pas été modifié. | Rien |
| Les routes littérales sont déclarées avant les routes paramétrées | OK | Ordre dans le fichier : `""` puis `"/{reservation_id}"` puis `"/{reservation_id}/annuler"`. Pas de conflit de chemin. | Rien |
| Réponse cohérente pour `POST /reservations/999/annuler` | OK | Testé : 404 avec le message "Réservation 999 introuvable". | Rien |

Aucune correction dans le code. Je pense que c'est en partie parce que mon `CLAUDE.md` donnait déjà les conventions du cours à l'agent (model_validator, response_model, def plutôt que async def). Le résultat aurait sûrement été moins propre sans ce fichier.

## Écarts et décisions

- Avant de coder, l'agent m'a posé deux questions au lieu de choisir tout seul.
- `ReservationUpdate` : mon CLAUDE.md impose trois schémas par ressource, mais aucune route ne modifie une réservation. J'ai choisi de ne pas le créer pour ne pas avoir de code inutile.
- `skip` : `GET /items` l'a mais la spec ne le prévoit pas pour les réservations. J'ai choisi de suivre la spec.
- L'agent a ajouté `ge=1` sur le filtre `item_id` de la liste alors que la spec ne le demandait pas. Je l'ai gardé parce qu'un id négatif n'a pas de sens, mais c'est un ajout qui n'était pas prévu.

## Limites connues

- On peut réserver un `item_id` qui n'existe pas, puisque la spec interdit d'accéder au stockage de `items`. Ça devrait se régler avec une clé étrangère quand on passera sur PostgreSQL.
- Rien n'empêche deux réservations actives sur le même item et le même créneau.
- Le 404 et le 409 n'apparaissent pas dans `/docs`. Il faudrait ajouter `responses=` sur les routes.
- L'erreur de dates renvoie `loc: ["body"]` sans le nom du champ, parce que le validateur porte sur tout le modèle. À prendre en compte pour les tests de la séance 2.

## Ce que je retiens du travail avec l'agent

Relire le plan avant d'accepter m'a permis de comparer chaque point à la spec avant qu'une seule ligne soit écrite. En validant les fichiers un par un, j'ai vérifié moi-même les points de contrôle du TP : le model_validator dans le schéma, les deux FAKE_DB séparés, l'ordre 404 puis 409 dans la route d'annulation.

Je retiens qu'un code qui marche n'est pas forcément conforme. Le ge=1 ajouté sur le filtre fonctionne très bien, mais il sortait de la spec, et je ne l'aurais pas remarqué sans relire le code ligne par ligne. La prochaine fois, je mettrai les limites connues (item inexistant, créneaux qui se chevauchent) directement dans la spec, pour qu'elles soient traitées ou assumées dès le départ.

## Seconde review avec GitHub Copilot (06/10/2026)

J'ai demandé à GitHub Copilot Chat de refaire la review avec la même grille. Sa réponse complète est dans `review-copilot.md`.

- Points communs : les 8 points de la grille sont OK, et il relève aussi l'item_id qui peut ne pas exister et l'absence de contrôle des chevauchements.
- Ce qu'il ajoute : le stockage en mémoire perdu au redémarrage, et la liste limitée d'exceptions pour la notification.
- Ce qu'il a raté : il conclut « aucun écart avec la spec » alors que le ge=1 sur le filtre item_id de la liste n'était pas demandé. Il ne voit pas non plus que le 404 et le 409 sont absents de /docs, ni que l'erreur de dates renvoie loc ["body"] sans nom de champ.

Conclusion : les deux agents se recoupent sur l'essentiel, mais aucun ne remplace une relecture ligne par ligne face à la spec. Croiser deux outils m'a surtout servi à confirmer mes propres constats.
