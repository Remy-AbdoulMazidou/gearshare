# Mesures EXPLAIN ANALYZE (séance 3, étape 5)

Mesures lancées par moi dans `psql`, sur la base du TP remplie avec environ 200 000 objets.
Texte mis en forme avec l'aide de Claude.

Chaque mesure est faite avec `EXPLAIN ANALYZE`, après un `ANALYZE items` quand un index vient
d'être créé.

## 1. Recherche exacte sur le titre

```sql
EXPLAIN ANALYZE SELECT * FROM items WHERE titre = 'Item de test 123456';
```

| Situation | Nœud | Temps d'exécution |
|---|---|---|
| Sans index | Seq Scan (200 003 lignes écartées par le filtre) | 17.951 ms |
| Avec `idx_items_titre` | Index Scan using idx_items_titre | 0.079 ms |

Facteur d'accélération : environ **227**.

Sans index, PostgreSQL lit toute la table pour trouver une seule ligne. Avec l'index B-tree, il
descend directement jusqu'à la bonne valeur.

## 2. Cas (a) : LIKE avec le joker au début

```sql
EXPLAIN ANALYZE SELECT * FROM items WHERE titre LIKE '%123456';
```

Résultat : Seq Scan, 11.417 ms, même avec `idx_items_titre`.

Explication : un B-tree est trié par le début de la chaîne, et ici le début est inconnu, donc
l'index ne permet pas de savoir où chercher.

## 3. Cas (b) : index sur une colonne booléenne

```sql
CREATE INDEX idx_items_disponible ON items (disponible);
ANALYZE items;
EXPLAIN ANALYZE SELECT * FROM items WHERE disponible = TRUE;
EXPLAIN ANALYZE SELECT * FROM items WHERE disponible = FALSE;
```

| Condition | Lignes trouvées | Nœud | Temps d'exécution |
|---|---|---|---|
| `disponible = TRUE` | 200 004 | Seq Scan | 27.200 ms |
| `disponible = FALSE` | 0 | Index Scan using idx_items_disponible | 0.140 ms |

Explication : toutes les lignes sont à `TRUE`, donc l'index ne filtre rien et le planificateur
préfère lire la table directement. Pour `FALSE`, la condition est très sélective (aucune ligne),
et l'index devient rentable.

Un index sur un booléen n'est donc utile que si la valeur cherchée est rare.

## 4. Question bonus : LIKE avec le joker à la fin

```sql
EXPLAIN ANALYZE SELECT * FROM items WHERE titre LIKE 'Item de test 12345%';
```

| Situation | Nœud | Lignes | Temps d'exécution |
|---|---|---|---|
| Avec `idx_items_titre` seul | Seq Scan | 11 | 20.929 ms |
| Avec `idx_items_titre_prefixe` (`varchar_pattern_ops`) | Index Scan using idx_items_titre_prefixe | 11 | 0.053 ms |

Réponse : non, l'index classique sur `titre` ne sert pas, alors que le joker est en fin de chaîne.

La raison est la collation de la base. La commande
`SELECT datcollate FROM pg_database WHERE datname = 'gearshare';` renvoie `en_US.utf8`. Avec
cette collation, l'ordre de tri ne suit pas l'ordre des caractères octet par octet, donc
PostgreSQL ne peut pas utiliser l'index pour un préfixe.

Avec un index créé avec `varchar_pattern_ops`, la comparaison se fait octet par octet, sans tenir compte de la collation.
PostgreSQL transforme alors le `LIKE` en intervalle, visible dans `Index Cond` :

```
titre ~>=~ 'Item de test 12345' AND titre ~<~ 'Item de test 12346'
```

```sql
CREATE INDEX idx_items_titre_prefixe ON items (titre varchar_pattern_ops);
ANALYZE items;
```

Facteur d'accélération : environ **395**.

## Ce que je retiens

- Un index B-tree classique aide pour l'égalité. Pour un préfixe, il faut `varchar_pattern_ops`
  avec notre collation. Un joker en début de chaîne n'utilise jamais l'index.
- Un index n'est utilisé que si la condition est sélective.
- La collation de la base change le comportement de `LIKE 'préfixe%'`.
- Il faut toujours mesurer avec `EXPLAIN ANALYZE` plutôt que supposer.