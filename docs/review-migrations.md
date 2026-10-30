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

## 2. Traduction des exceptions métier (étape 4)

Choix : un gestionnaire d'exceptions global dans `main.py`, plutôt qu'un `try`/`except` dans
chaque route. La correspondance entre exception métier et code HTTP (introuvable → 404, conflit →
409, accès refusé → 403) est écrite une seule fois, et les routes restent de simples traducteurs
entre schémas et service.

## 3. Point de contrôle de l'étape 1 : erreur après un ajout

Test : `POST /items` avec `owner_id: 999`, un utilisateur qui n'existe pas.

- Avant correction : `500 Internal Server Error`. L'`IntegrityError` de PostgreSQL (clé
  étrangère) remontait jusqu'à `get_db`, qui faisait un `rollback`. `SELECT count(*) FROM items`
  donnait toujours 3 : rien n'avait été écrit.
- Ce n'était pas le bon code : l'erreur vient du client, pas du serveur. C'est au service de la
  détecter avant d'écrire en base.
- Correction : `UserRepository.get` et une vérification dans `ItemService` avant la création, le
  remplacement ou le changement de propriétaire. Réponse obtenue :
  `404 {"detail": "Utilisateur 999 introuvable"}`, et toujours 3 items en base.

La base reste le dernier garde-fou (clé étrangère, `rollback` dans `get_db`), mais le message
clair vient du service.

## 4. Le N+1 sur `GET /items` (étape 5)

`ItemRead` contient maintenant le propriétaire (`OwnerRead` : `id` et `display_name` seulement,
ni email ni `password_hash`).

Données de test : 20 utilisateurs et 20 items insérés avec `INSERT ... SELECT` et
`generate_series`, chaque item avec un propriétaire différent. Avec un seul propriétaire, la
session SQLAlchemy ne le chargerait qu'une fois et le N+1 ne se verrait pas.

Mesure avec `SQL_ECHO=true` :

```bash
curl -s "http://localhost:8000/items?limit=50" > /dev/null
docker compose logs --since 30s backend | grep -c "SELECT"
```

| | Requêtes `SELECT` pour une page de 23 items |
|---|---|
| Avant | 22 (1 pour la liste, 21 pour les propriétaires) |
| Après `selectinload(Item.owner)` | 2 (la liste, puis tous les propriétaires en une fois avec `WHERE users.id IN (...)`) |

Origine : aucune boucle dans le code. C'est la sérialisation de la réponse qui lit `item.owner`
pour construire chaque `ItemRead`. La relation est chargée à la demande (lazy loading), donc une
requête par propriétaire différent.

Correction dans `ItemRepository.list` :

```python
stmt = select(Item).options(selectinload(Item.owner))
```

`SQL_ECHO` remis à `false` après la mesure.

## 5. Le frontend sur la vraie base (étape 6.4)

Parcours du TP 1 refait sur `http://localhost:8080` après le passage du backend sur PostgreSQL.

- Liste et détail : aucune modification du frontend. Le contrat de lecture n'a pas changé. Le
  champ `owner` ajouté à `ItemRead` est simplement ignoré par les templates. `tarif_jour` reste
  un `float` dans `ItemRead`, il s'affiche donc comme avant (`20.0 €`).
- Création : refusée avec « owner_id : Field required ». Changement de contrat, un item a
  désormais un propriétaire obligatoire. Le frontend a affiché proprement l'erreur 422 du backend
  au-dessus du formulaire, comme prévu au TP 1.

Seule modification du frontend, dans `frontend/app/routers/items.py`, route `POST /items` :

```python
"owner_id": 1,  # TODO séance 5 : remplacé par l'utilisateur connecté, déduit du jeton
```

avec l'utilisateur de démonstration inséré par `psql` (`demo@esiee.fr`, id 1). Correction
provisoire : en séance 5, le backend déduira le propriétaire du jeton et ce champ disparaîtra.

Vérifié : création de deux objets depuis le frontend, puis `docker compose restart`. Les objets
sont toujours dans la liste, contrairement à l'étape 6 du TP 1 où le stockage en mémoire était
vidé au redémarrage.
