# Review des migrations (séance 4, TP 2)

Manipulations faites par moi dans le terminal. Texte mis en forme avec l'aide de Claude.

## 1. Le piège du renommage (étape 3bis)

### Situation de départ

Base migrée avec `7f3fbd8a28c3_schema_initial`. Deux items insérés avec `psql` pour l'utilisateur
`alice@esiee.fr` : « Vélo de ville » à 8.50 et « Perceuse » à 5.00.

Dans le modèle `Item`, j'ai renommé l'attribut `tarif_jour` en `prix_jour`, puis lancé :

```bash
docker compose run --rm backend alembic revision --autogenerate -m "renommage tarif_jour"
```

### Migration générée

```python
def upgrade() -> None:
    op.add_column('items', sa.Column('prix_jour', sa.Numeric(precision=8, scale=2), nullable=False))
    op.drop_column('items', 'tarif_jour')


def downgrade() -> None:
    op.add_column('items', sa.Column('tarif_jour', sa.NUMERIC(precision=8, scale=2), autoincrement=False, nullable=False))
    op.drop_column('items', 'prix_jour')
```

### Ce qu'elle aurait fait

Alembic ne détecte pas un renommage. Il compare le modèle et la base, voit une colonne qui
disparaît et une colonne qui apparaît, et génère un ajout puis une suppression.

- `add_column` en `nullable=False` sur une table qui contient déjà deux lignes : PostgreSQL
  refuse, car ces lignes auraient `NULL` dans `prix_jour`. La migration échoue.
- Si elle passait (table vide, ou colonne en `nullable=True`), `drop_column('tarif_jour')`
  supprimerait les tarifs. Les deux items perdraient leur prix, sans message d'erreur.

Le `downgrade()` a le même défaut dans l'autre sens.

### Correction à la main

```python
def upgrade() -> None:
    op.alter_column("items", "tarif_jour", new_column_name="prix_jour")


def downgrade() -> None:
    op.alter_column("items", "prix_jour", new_column_name="tarif_jour")
```

`alter_column` avec `new_column_name` produit un `ALTER TABLE items RENAME COLUMN`, les données
restent en place.

### Vérification

```
 id |     titre     | prix_jour
----+---------------+-----------
  1 | Vélo de ville |      8.50
  2 | Perceuse      |      5.00
```

Ensuite, retour en arrière : `alembic downgrade -1`, suppression du fichier de migration,
`tarif_jour` remis dans le modèle. `alembic check` ne détecte plus aucune différence entre le
modèle et la base.

### Ce que je retiens

Une migration autogénérée est un brouillon. Il faut toujours la relire avant de l'appliquer,
surtout quand une colonne est supprimée : `drop_column` détruit des données.
