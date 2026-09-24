# Journal des sessions

Une entrée par session de travail, la plus récente en bas.

## 2026-09-23 · Initialisation

- Fait par : Rémy
- Création du dépôt à partir du `projet-demo` de la séance 1.
- Mise en place de `CLAUDE.md`, du suivi (`docs/suivi/`) et des commandes `/reprendre` et `/cloturer`.

## 2026-09-24 · TP séance 1, étapes 1 à 4

- Fait par : Claude Code pour le code, Rémy pour les tests et les commits.
- Étape 1 : route `GET /items/{item_id}` avec `Path(ge=1)`.
- Étape 2 : route `GET /items` avec `skip`, `limit` (plafonné à 100), `q` et `disponible`.
- Étape 3 : `app/schemas/item.py` (`ItemCreate`, `ItemRead`) avec `extra="forbid"`,
  stockage `FAKE_DB` en mémoire et `POST /items` en 201.
- Étape 4 : `ItemUpdate`, filtres et pagination réels sur `GET /items`, `GET`/`PUT`/`PATCH`
  unitaires avec 404, `DELETE` en 204 sans corps.
- Quatre commits, un par étape. Étapes 5 et 6 volontairement non faites.
- Problème rencontré : le TP laisse entendre que `disponible=oui` est accepté comme booléen.
  En réalité Pydantic v2 n'accepte que les valeurs anglaises (`true`, `yes`, `on`, `1`,
  `false`, `no`, `off`, `0`) ; `oui` renvoie donc 422, comme `peut-etre`.
- Vérification faite par Rémy : `exclude_unset=True` retiré du `PATCH` pour observer le bug,
  la `description` était bien écrasée à `null`, puis remis en place.
- Corrections de Rémy : aucune sur le code, l'arbre de travail committé est identique à ce qui
  a été produit. Seul le message du commit de l'étape 1 a été reformulé.
