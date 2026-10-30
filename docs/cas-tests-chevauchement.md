# Cas de tests du chevauchement de réservations (séance 4, TP 2, étape 7)

Cas rejoués par moi avec `curl` sur l'API. Texte mis en forme avec l'aide de Claude.

## Règle

Une réservation demandée `[D_début, D_fin)` est en conflit avec une réservation **active** du
même item `[E_début, E_fin)` si :

```text
D_début < E_fin  ET  D_fin > E_début
```

Il n'y a pas de conflit dans deux cas seulement : la demande finit avant le début de l'existante
(`D_fin ≤ E_début`), ou elle commence après sa fin (`D_début ≥ E_fin`). La condition de conflit
est la négation de ces deux cas, elle couvre donc aussi le cas englobant.

Décision : deux réservations jointives (l'une finit le jour où l'autre commence) ne sont **pas**
en conflit. Les comparaisons sont strictes (`<`, `>`), comme le `'[)'` de la contrainte `EXCLUDE`
de la séance 3. Un objet rendu le 15 peut être réservé à partir du 15.

## Résultats

Item neuf (« Vélo test chevauchement »), réservation de référence active du 10/11/2026 au
15/11/2026, emprunteur 1.

| Cas | Existante | Demandée | Code attendu | Code obtenu |
|---|---|---|---|---|
| Référence | aucune | 10/11 → 15/11 | 201 | 201 |
| Avant | 10/11 → 15/11 | 05/11 → 08/11 | 201 | 201 |
| Après | 10/11 → 15/11 | 20/11 → 25/11 | 201 | 201 |
| Partiel au début | 10/11 → 15/11 | 08/11 → 12/11 | 409 | 409 |
| Partiel à la fin | 10/11 → 15/11 | 13/11 → 18/11 | 409 | 409 |
| Englobant | 10/11 → 15/11 | 08/11 → 20/11 | 409 | 409 |
| Jointif | 10/11 → 15/11 | 15/11 → 20/11 | 201 | 201 |
| Item inexistant | | `item_id` 9999 | 404 | 404 |

Les créneaux « avant » et « après », acceptés, ne chevauchent aucun des cas suivants : seul le
créneau de référence explique les 409.

Vérifié aussi dans le navigateur, sur la page de détail d'un item : un chevauchement affiche
« Le créneau demandé est déjà réservé » au-dessus du formulaire, avec les dates conservées, et le
cas jointif est accepté.

## Automatisation

Les mêmes cas sont automatisés dans `backend/tests/test_reservations.py`
(`test_service_refuse_les_chevauchements_et_accepte_les_autres`, paramétré sur
`ReservationService`).
