# Seconde review de la ressource reservations avec GitHub Copilot

Faite le 06/10/2026 avec GitHub Copilot Chat dans VS Code, en mode Ask (lecture seule, aucun fichier modifié).
Prompt et réponse copiés tels quels. La comparaison avec ma propre review est dans `REVIEW.md`.

## Prompt envoyé

```
Fais la review de la ressource reservations implémentée dans #file:backend/app/routers/reservations.py et #file:backend/app/schemas/reservation.py, par rapport à la spécification #file:docs/tp/seance-1/SPEC-reservations.md.

Pour chaque point de cette grille, réponds OK ou KO avec une justification courte :
1. Codes de statut conformes à la spec (201, 404, 409)
2. response_model présent sur les 4 routes
3. Validation date_fin > date_debut dans le schéma Pydantic
4. Le router n'accède pas au stockage de items
5. Pas d'async def sans await
6. Aucune dépendance ajoutée
7. Routes littérales déclarées avant les routes paramétrées
8. Réponse cohérente pour POST /reservations/999/annuler

Ensuite, liste les écarts avec la spec et les limites que tu vois. Ne modifie aucun fichier.
```

## Réponse de Copilot

Je vais comparer directement les deux fichiers d'implémentation à la spécification, puis vérifier les 8 critères un par un et relever les limites restantes. Je reste en lecture seule comme demandé.

La comparaison locale est déjà assez nette : les deux schémas couvrent la validation demandée et les quatre routes déclarent un `response_model`. Je vérifie maintenant les tests et les dépendances pour distinguer les écarts réels à la spec des limites générales de cette implémentation en mémoire.

**Grille**

1. **OK** — POST crée en `201`; absence en `404`; annulation déjà effectuée en `409`. Voir `reservations.py:29-67`.
2. **OK** — Les 4 routes ont un `response_model`.
3. **OK** — `model_validator` rejette `date_fin <= date_debut` dans `reservation.py:10-19`.
4. **OK** — Le router utilise uniquement son propre `FAKE_DB`; aucun accès au stockage des items.
5. **OK** — Toutes les routes sont synchrones (`def`), sans `async def`.
6. **OK** — Aucune dépendance supplémentaire visible dans `requirements.txt`.
7. **OK** — Les routes sans paramètre sont déclarées avant `/{reservation_id}` et `/{reservation_id}/annuler`.
8. **OK** — `POST /reservations/999/annuler` renvoie `404`, conformément à la spec.

**Écarts avec la spec**

Aucun écart fonctionnel identifié sur les points explicitement décrits dans `SPEC-reservations.md`.

**Limites**

- `item_id` est validé comme entier positif, mais l'existence réelle de l'item n'est pas vérifiée. Une réservation peut donc référencer un item inexistant.
- Les chevauchements de créneaux ne sont pas détectés. La spec ne l'exige pas explicitement.
- Le stockage est un dictionnaire en mémoire : les réservations sont perdues au redémarrage et ne sont pas adaptées à plusieurs processus.
- La notification d'annulation est une simulation locale ; les erreurs prises en charge sont limitées à `ConnectionError` et `TimeoutError`.
- La revue est statique : les tests présents couvrent ces comportements, mais je ne les ai pas exécutés.
