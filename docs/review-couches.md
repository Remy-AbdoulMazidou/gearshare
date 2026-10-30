# Review de la verticale `reservations` (séance 4, TP 2, étape 7.4)

Relue par moi, seul (pas de binôme), en vérifiant chaque point dans le code et avec des tests
manuels. Texte mis en forme avec l'aide de Claude. Le code de la verticale a été écrit par GitHub
Copilot (mode Agent), prompt dans `docs/tp/seance-4/prompts.md`.

| Point de contrôle | OK / KO | Ce que j'ai vérifié ou corrigé |
|---|---|---|
| Aucun SQL ni requête SQLAlchemy dans le router | OK | Le router construit le service et appelle ses méthodes, aucun `select` |
| Aucune `HTTPException` dans le service (uniquement les exceptions métier) | OK | `RessourceIntrouvable` et `ConflitMetier`, traduites par le gestionnaire global de `main.py` |
| Aucun `commit()` dans le repository | OK | `add` fait `flush()` et `refresh()`, le `commit()` reste dans `get_db` |
| `response_model` sur les 4 routes | OK | Aussi sur `POST /reservations/{id}/annuler`, gardée pour les tests de la séance 2 |
| Schéma de lecture construit depuis l'objet SQLAlchemy, sans champ interne | OK | `ReservationRead` en `from_attributes`, uniquement les colonnes de la réservation |
| La requête de chevauchement couvre les cinq cas, y compris l'englobant | OK | Condition `date_debut < date_fin demandée` et `date_fin > date_debut demandée`, cas rejoués dans `docs/cas-tests-chevauchement.md` et test paramétré |
| Pas de f-string dans une requête SQL | OK | Les f-strings du service ne servent qu'aux messages d'exception |
| Pas de N+1 sur `GET /reservations` (si la relation `item` est chargée) | OK | `ReservationRead` n'expose pas la relation `item`, une seule requête par page |
| Migration relue, `downgrade()` testé | OK | Pas de nouvelle migration : `reservations` existait déjà dans `7f3fbd8a28c3`, dont l'aller-retour a été testé à l'étape 3 |
| Aucune dépendance ajoutée sans justification | OK | Seulement `logging` (bibliothèque standard) pour la notification |

## Limites relevées

- **Deux requêtes simultanées.** Le service vérifie le chevauchement, puis insère. Si deux
  réservations du même créneau arrivent exactement en même temps, les deux vérifications peuvent
  passer avant l'insertion. La base ne l'empêche pas encore : la contrainte `EXCLUDE` de la
  séance 3 n'existe que dans `tp-db/`, pas dans les migrations Alembic. Correction possible : une
  migration qui ajoute `btree_gist` et la même contrainte `EXCLUDE`. Le service garderait sa
  vérification pour renvoyer un message clair, et la base deviendrait le dernier garde-fou.
- **Notification avant le commit.** L'annulation envoie la notification dans le service, avant le
  `commit()` fait par `get_db` en fin de requête. Si le commit échouait, la notification serait
  partie pour une annulation non enregistrée. Acceptable tant que la notification ne fait qu'un
  log, à revoir si elle devient un vrai envoi.
