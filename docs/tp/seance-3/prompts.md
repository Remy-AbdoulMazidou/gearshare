# Prompts de la séance 3

## Étape 6 : DDL du schéma v2

Outil : GitHub Copilot, mode Agent, dans VS Code.

### Prompt 1 : création de 03-schema-v2.sql

```text
Dans tp-db/sql/init/, crée le fichier 03-schema-v2.sql qui étend le schéma de 01-schema.sql (tables users, items, reservations), pour PostgreSQL 16.

Règles métier à traduire :
1. Après une réservation au statut 'terminee', l'emprunteur peut laisser un avis : une note entière de 1 à 5 et un commentaire optionnel.
2. Un avis est lié à exactement une réservation, et une réservation ne peut avoir qu'un seul avis.
3. Un item peut avoir plusieurs tags et un tag peut être sur plusieurs items. Le libellé d'un tag est unique et en minuscules.
4. Un même item ne peut pas avoir deux réservations actives qui se chevauchent. Utilise une contrainte EXCLUDE avec l'extension btree_gist.

Contraintes techniques : toutes les contraintes sont nommées, TIMESTAMPTZ pour les horodatages, un index sur chaque clé étrangère, un ON DELETE explicite sur chaque clé étrangère, aucun type flottant pour un montant.
Le fichier doit s'exécuter juste après 01-schema.sql et 02-seed.sql au premier démarrage du conteneur.
Pas de commentaires inutiles. Ne modifie aucun autre fichier et ne fais pas de commit.
```

Résultat : fichier créé et testé par Copilot dans un conteneur PostgreSQL 16 temporaire. Il
avait en plus renommé toutes les contraintes existantes, ajouté deux index en double et un
trigger commun aux tables `avis` et `reservations`.

### Prompt 2 : corrections après review

```text
Corrige 03-schema-v2.sql après ma review :
1. Supprime tous les RENAME CONSTRAINT. Les noms dates_coherentes et statut_valide sont déjà utilisés dans mes tests de l'étape 2 et seront interceptés côté API. Garde le DROP/ADD de reservations_borrower_fk qui rend le ON DELETE RESTRICT explicite.
2. Supprime avis_reservation_id_idx : la contrainte UNIQUE avis_reservation_uq crée déjà un index sur reservation_id.
3. Supprime item_tags_item_id_idx : la clé primaire (item_id, tag_id) commence par item_id, son index suffit.
4. Simplifie le trigger : la fonction verifier_avis_reservation_terminee() ne sert qu'à la table avis (BEFORE INSERT OR UPDATE OF reservation_id). Supprime le trigger sur reservations et la branche TG_TABLE_NAME.
Ne modifie aucun autre fichier et ne fais pas de commit.
```

Ensuite, correction à la main de la condition du trigger (`EXISTS ... statut <> 'terminee'`),
pour que l'avis sur une réservation inexistante soit refusé par la clé étrangère. Détails dans
`tp-db/REVIEW-schema.md`.
