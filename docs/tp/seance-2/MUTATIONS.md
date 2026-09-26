# Tests de mutation (cours séance 2, section 8)

Mutations lancées et résultats observés par moi. Tableau mis en forme avec l'aide de Claude.

Méthode : pour chaque règle, j'introduis un bug avec `sed`, je lance `pytest`, je note les tests qui passent au rouge, puis je remets le code d'origine avec `git checkout`. À la fin, `git status` est propre et les 48 tests repassent.

| # | Règle protégée | Mutation introduite | Tests rouges | Détectée ? |
|---|---|---|---|---|
| 1 | Refus d'une double annulation (409) | `if reservation["statut"] == "annulee":` remplacé par `if False:` | `test_annuler_reservation_deja_annulee_renvoie_409` (200 au lieu de 409) | Oui |
| 2 | `date_fin` strictement après `date_debut` | `<=` remplacé par `<` dans le `model_validator` | `test_creer_reservation_avec_dates_invalides_renvoie_422`, cas dates égales seulement (201 au lieu de 422) | Oui |
| 3 | Champs inconnus refusés (`extra="forbid"`) | Ligne `model_config` retirée de `ItemCreate` et `ItemUpdate` | `test_creer_item_invalide_renvoie_422[couleur]` (201) et `test_modifier_item_invalide_renvoie_422[couleur]` (200) | Oui |
| 4 | Pagination plafonnée à 100 | `le=100` remplacé par `le=1000` | `test_lister_items_avec_parametres_invalides_renvoie_422[limit=101]` (200 au lieu de 422) | Oui |

Couverture avant et après : 100 %. Elle ne changeait rien à ces résultats, puisqu'elle mesure le code exécuté et pas le code vérifié.

## Observations

- Mutation 2 : le cas des dates inversées est resté vert. Seul le cas des dates égales a détecté le bug. Le test unitaire de `test_schemas.py` ne teste que des dates inversées, il ne l'aurait pas vu.
- Mutation 4 : le test utilise `limit=101`, la valeur juste au-dessus de la borne. N'importe quel relâchement du plafond est donc détecté, alors qu'un test avec `limit=500` laisserait passer un plafond relevé à 1000.
- Mutation 3 : les deux schémas sont protégés séparément, un test par schéma.
- Un contrôle en plus a été fait par l'agent pendant l'étape 2 : sans `exclude_unset=True`, `test_patch_partiel_conserve_les_autres_champs` passe au rouge.

## Ce que j'en retiens

Avoir 100 % de couverture ne prouvait pas que mes tests étaient bons. Ce sont les mutations qui m'ont montré quelles règles étaient vraiment protégées.

La mutation 2 est celle qui m'a le plus appris : si je n'avais testé que des dates inversées, le bug sur les dates égales serait passé. Je teste maintenant la valeur juste à la limite (dates égales, limit=101) en plus d'un cas évident. Je garderai cette méthode pour les prochaines séances, en cassant au moins les règles les plus importantes de chaque nouvelle ressource.
