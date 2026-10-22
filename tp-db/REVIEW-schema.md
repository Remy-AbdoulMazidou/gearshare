# Review du schéma v2 (séance 3, étape 6)

Le DDL de `sql/init/03-schema-v2.sql` a été écrit par GitHub Copilot en mode Agent, à partir des
règles du TP (prompts dans `docs/tp/seance-3/prompts.md`). Je l'ai relu avec la grille du prof,
avec l'aide de Claude. Copilot a appliqué les corrections de la review, puis j'ai corrigé le
trigger à la main. Les tests sont dans `sql/tests-contraintes.sql`.

## Grille

| Point de contrôle | OK / KO | Ce que j'ai corrigé |
|---|---|---|
| Chaque table a une clé primaire | OK | `avis_pk`, `tags_pk`, `item_tags_pk` |
| Les clés étrangères sont déclarées avec `REFERENCES` | OK | |
| Les `ON DELETE` sont explicites et cohérents avec le métier | KO puis OK | `borrower_id` n'avait pas de `ON DELETE` dans `01-schema.sql`. Il est maintenant en `RESTRICT` explicite (voir la décision plus bas) |
| La règle « un seul avis par réservation » est garantie par une contrainte `UNIQUE` | OK | `avis_reservation_uq` |
| La note est bornée par un `CHECK (note BETWEEN 1 AND 5)` | OK | `avis_note_ck` |
| La table de liaison item/tag a une clé primaire composite | OK | `item_tags_pk (item_id, tag_id)` |
| Le libellé de tag est `UNIQUE` | OK | `tags_libelle_uq`, plus `tags_libelle_minuscule_ck` pour les minuscules |
| Les contraintes sont nommées | OK | Copilot renommait aussi toutes les contraintes de `01-schema.sql`. J'ai retiré ces renommages, parce que `dates_coherentes` et `statut_valide` sont déjà utilisés dans mes tests de l'étape 2 et seront interceptés par l'API |
| Des index existent sur les clés étrangères | OK après correction | Deux index en double retirés : `avis(reservation_id)` est déjà indexé par la contrainte `UNIQUE`, et `item_tags(item_id)` par la clé primaire composite qui commence par `item_id` |
| Le non-chevauchement est réellement garanti (contrainte) ou explicitement laissé à l'applicatif | OK | Contrainte `reservations_active_no_overlap` (voir plus bas) |
| Aucun type flottant pour un montant, aucun `TIMESTAMP` sans fuseau | OK | `NUMERIC(8, 2)` pour le tarif, `TIMESTAMPTZ` pour `created_at` |

## Non-chevauchement des réservations

Garanti en base avec une contrainte d'exclusion :

```sql
EXCLUDE USING gist (
    item_id WITH =,
    daterange(date_debut, date_fin, '[)') WITH &&
) WHERE (statut = 'active')
```

- `btree_gist` est nécessaire pour utiliser `=` sur un `BIGINT` dans un index GiST.
- `'[)'` exclut `date_fin` : un objet rendu le 5 peut être réservé à partir du 5, comme dans l'API.
- `WHERE (statut = 'active')` : une réservation annulée ne bloque plus les dates.

L'API garde quand même sa vérification pour renvoyer un message clair, mais la base reste le
dernier garde-fou si deux requêtes arrivent en même temps.

## Avis seulement après une réservation terminée

Un `CHECK` ne peut pas lire une autre table, donc cette règle passe par un trigger
`BEFORE INSERT OR UPDATE OF reservation_id` sur `avis`. Il bloque seulement si la réservation
existe et n'est pas terminée. Si elle n'existe pas, c'est la clé étrangère `avis_reservation_fk`
qui refuse, avec son nom dans le message.

Problème trouvé grâce aux tests : ma première correction gardait `NOT EXISTS` avec la condition
`statut <> 'terminee'`, ce qui inversait la règle. Les tests 1, 2 et 4 échouaient pour la
mauvaise raison et l'avis sur une réservation active passait. Corrigé en `EXISTS`, puis base
reconstruite avec `down -v` et `up -d`.

Limite connue : le trigger ne bloque pas le passage d'une réservation avec avis vers un autre
statut. `terminee` est un statut final, donc ce cas sera refusé par l'API.

## Suppression d'un compte

Le test avec `ON DELETE CASCADE` a montré que supprimer Bob effaçait aussi l'historique d'Alice
et de Chloé, via la double cascade `users → items → reservations`. Pour GearShare, un compte
supprimé sera donc désactivé et anonymisé (`actif = FALSE`, nom et email remplacés) au lieu
d'être effacé. L'historique des prêts reste intact pour les autres utilisateurs, et les données
personnelles disparaissent. La clé `borrower_id` est en `ON DELETE RESTRICT` comme garde-fou.
