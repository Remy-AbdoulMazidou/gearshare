# Comment appliquer les migrations au démarrage (séance 4, TP 2, étape 6.2)

Expériences lancées par moi dans le terminal. Texte mis en forme avec l'aide de Claude.

## Mon choix : un service `migrate` (option 2)

```yaml
  migrate:
    build: ./backend
    env_file: .env
    depends_on:
      db:
        condition: service_healthy
    command: alembic upgrade head

  backend:
    depends_on:
      db:
        condition: service_healthy
      migrate:
        condition: service_completed_successfully
```

`migrate` est construit depuis la même image que le backend. Il attend que PostgreSQL soit prêt,
applique les migrations, puis s'arrête. Le backend ne démarre que si `migrate` s'est terminé avec
le code 0.

### Vérification depuis zéro (étape 6.3)

```bash
docker compose down -v
docker compose up --build -d
docker compose ps -a
```

| Service | Statut |
|---|---|
| `db` | `Up (healthy)` |
| `migrate` | `Exited (0)`, log `Running upgrade  -> 7f3fbd8a28c3, schema initial` |
| `backend` | `Up`, démarré après `migrate` |
| `frontend` | `Up` |

`SELECT * FROM alembic_version` renvoie `7f3fbd8a28c3`. La base `gearshare_test` est créée par le
script `db/init/01-create-test-database.sql` au premier démarrage du volume.

## Les quatre questions

### 1. Que se passe-t-il au deuxième `docker compose up`, quand la base est déjà à jour ?

Testé avec un second `docker compose up -d`. `migrate` est relancé et se termine en
`Exited (0)`, mais ses logs n'affichent pas de nouvelle ligne `Running upgrade`. Alembic lit la
table `alembic_version`, voit que la base est déjà à `head` et ne fait rien. `upgrade head` est
idempotent. Le backend, déjà démarré, n'est pas relancé.

### 2. Si une migration échoue, que voit-on ? Le backend démarre-t-il quand même ?

Testé avec une migration cassée volontairement
(`ALTER TABLE table_inexistante ADD COLUMN x INTEGER`), puis `docker compose down` et `up -d` :

- `docker compose up` affiche `service "migrate" didn't complete successfully: exit 1` ;
- `docker compose ps -a` montre `migrate` en `Exited (1)`, et `backend` et `frontend` en
  `Created`, c'est-à-dire jamais démarrés ;
- `/health` ne répond pas ;
- `docker compose logs migrate` donne l'erreur exacte :
  `relation "table_inexistante" does not exist`, avec la requête SQL.

Le backend ne démarre donc pas sur une base mal migrée. Après suppression de la migration cassée,
`alembic_version` valait toujours `7f3fbd8a28c3` : PostgreSQL exécute la migration dans une
transaction (« Will assume transactional DDL »), rien n'est appliqué à moitié.

### 3. En production, trois instances du backend démarrent en même temps sur une base pas encore migrée

Non testé en local (le port `8000` publié empêche de lancer plusieurs instances).

Avec un service `migrate`, la migration tourne une seule fois, avant le démarrage des backends.
Les trois instances attendent sa réussite, puis démarrent sur une base déjà à jour.

Avec un `entrypoint.sh` (option 1), chaque instance lancerait `alembic upgrade head` en même
temps. La première créerait les tables, les autres échoueraient sur des tables déjà existantes ou
attendraient des verrous, et certaines instances s'arrêteraient en erreur au démarrage.

### 4. Le backend tourne en `--reload` : l'option fonctionne-t-elle toujours ?

Oui. Le service `backend` garde sa commande `uvicorn ... --reload`, la migration est dans un autre
service. Testé avec `touch backend/app/main.py` : les logs du backend affichent
`WatchFiles detected changes in 'app/main.py'. Reloading...`.

Le `--reload` recharge seulement le code Python, il ne rejoue pas les migrations. Après avoir
ajouté une migration pendant le développement, on l'applique sans toucher à l'API avec :

```bash
docker compose run --rm migrate
```

Testé : sur une base à jour, la commande se termine sans `Running upgrade`.

## Justification

Je garde le service `migrate` pour trois raisons :

1. La migration ne tourne qu'une fois, même avec plusieurs instances du backend (question 3).
2. Un échec est visible tout de suite (`Exited (1)` dans `docker compose ps -a`) et bloque le
   démarrage de l'API, au lieu de la laisser tourner sur une base incohérente (question 2).
3. Les responsabilités sont séparées : la migration a ses propres logs et se relance seule avec
   `docker compose run --rm migrate`, sans redémarrer l'API (question 4).

L'inconvénient est un service de plus dans `docker-compose.yml`, ce qui me paraît négligeable.
