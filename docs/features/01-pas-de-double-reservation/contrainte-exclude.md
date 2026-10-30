# Contrainte EXCLUDE dans les migrations Alembic

Expériences lancées par moi dans le terminal. Texte mis en forme avec l'aide de Claude.

## Le problème

Limite relevée dans `docs/review-couches.md` : le service vérifie le chevauchement avec
`has_active_overlap`, puis insère. Deux requêtes simultanées peuvent passer la vérification avant
que l'une des deux n'insère. La contrainte `EXCLUDE` de la séance 3 n'existait que dans `tp-db/`.

## Qui a fait quoi

| Partie | Fait par |
|---|---|
| `ExcludeConstraint` dans `backend/app/models/reservation.py` | Moi |
| Migration `282ac4d65b77` écrite à la main | Moi |
| `btree_gist` dans `conftest.py`, traduction en 409 dans le repository, 4 tests | GitHub Copilot (mode Agent), prompt dans `prompts.md` |
| Simplification de la condition sur `constraint_name` après review | Moi |
| Vérifications, mutation, course entre deux sessions `psql` | Moi |

## Ce que j'ai constaté

**Avant de migrer.** Requête de recherche de chevauchements actifs sur la base de dev :
`(0 rows)`. Sinon la création de la contrainte aurait été refusée.

**Autogenerate ne voit pas la contrainte.** Après l'ajout de `ExcludeConstraint` dans le modèle,
`alembic revision --autogenerate` a produit une migration avec seulement `pass`. Alembic ne compare
pas les contraintes `EXCLUDE`. Même leçon que le renommage de la séance 4 : une migration générée
se relit toujours. J'ai écrit `upgrade()` en SQL avec `op.execute`, car
`op.create_exclude_constraint` ne gère pas l'expression `daterange(...)`.

```sql
CREATE EXTENSION IF NOT EXISTS btree_gist;
ALTER TABLE reservations
ADD CONSTRAINT reservations_active_no_overlap
EXCLUDE USING gist (
    item_id WITH =,
    daterange(date_debut, date_fin, '[)') WITH &&
) WHERE (statut = 'active');
```

**Aller-retour.** `upgrade` (`7f3fbd8a28c3 -> 282ac4d65b77`), contrainte visible dans
`\d reservations`, `downgrade -1`, `upgrade` à nouveau, puis `alembic check` :
`No new upgrade operations detected.`

**Tests.** Avant la correction de Copilot : `6 failed, 8 passed, 86 errors`, avec
`data type bigint has no default operator class for access method "gist"`. La base de test est
créée par `create_all` et pas par Alembic, l'extension n'y était donc pas. Après : `104 passed`.

**Review.** Copilot avait écrit `getattr(getattr(exc.orig, "diag", None), "constraint_name", None)`.
Avec psycopg, `exc.orig.diag` existe toujours. J'ai simplifié en
`exc.orig.diag.constraint_name == EXCLUDE_CONSTRAINT_NAME`.

**Mutation.** Nom de contrainte remplacé par `"nom_faux"` dans le repository :
`test_course_sur_la_contrainte_exclude_renvoie_409` échoue (l'erreur remonte au lieu d'un 409).
Nom remis : `104 passed`.

**Vraie course entre deux sessions `psql`.**

1. A : `BEGIN`, insertion d'une réservation du 01/03 au 05/03/2030 sur l'item 1, sans `COMMIT`.
2. B : `BEGIN`, insertion du 03/03 au 08/03/2030 sur le même item. B reste bloqué.
3. A : `COMMIT`. B reçoit aussitôt
   `ERROR: conflicting key value violates exclusion constraint "reservations_active_no_overlap"`.
4. B : `ROLLBACK`. Une seule réservation en base, celle de A. Ligne de test supprimée ensuite.

B attend car l'index de la contrainte voit la ligne non validée de A. PostgreSQL ne peut pas
décider avant de savoir si A valide ou annule.

## Pourquoi garder les deux vérifications

- `has_active_overlap` dans le service traite le cas courant avec un message clair, sans erreur
  SQL.
- La contrainte en base est le dernier garde-fou en cas de course. Le repository la traduit en
  `ConflitMetier`, donc l'API répond 409 avec le même message et jamais 500.
- Le savepoint (`begin_nested`) annule seulement l'insertion ratée. La session reste utilisable.
