# Prompts de la séance 5

## Étape 1 : hachage des mots de passe

```text
Étape 1 du TP ../cours/seances/seance-5-authentification/tp/README.md, en suivant le cours ../cours/seances/seance-5-authentification/cours/README.md.

- backend/app/core/security.py : hash_password et verify_password. PBKDF2-HMAC-SHA256 de hashlib, 600 000 itérations, sel de 16 octets tiré avec secrets. Condensat auto-descriptif dans une seule chaîne (algorithme, nombre d'itérations, sel, condensat). verify_password relit le nombre d'itérations dans la chaîne stockée, compare en temps constant avec hmac.compare_digest, et renvoie False sans lever d'exception sur un condensat malformé.
- backend/tests/test_security.py, sans base ni client HTTP : deux hachages du même mot de passe sont différents, le bon mot de passe est accepté et un mauvais refusé, un condensat malformé ("x") est refusé sans erreur, un condensat produit avec un autre nombre d'itérations reste vérifiable.

Lance docker compose run --rm backend pytest tests/test_security.py -v, puis toute la suite. Ne touche ni aux routers ni au frontend. Pas de commentaires inutiles, ne fais pas de commit. Respecte .github/copilot-instructions.md pour le journal. Ajoute ce prompt tel quel à la fin de docs/tp/seance-5/prompts.md (crée le fichier avec un titre « Prompts de la séance 5 »), sous le titre « Étape 1 : hachage des mots de passe ».
```

## Étape 2 : inscription

```text
Étape 2 du TP ../cours/seances/seance-5-authentification/tp/README.md, en suivant le cours ../cours/seances/seance-5-authentification/cours/README.md et en respectant les couches existantes.

- backend/app/schemas/user.py : UserCreate (email validé avec EmailStr, password de 12 à 128 caractères, display_name), UserRead sans password_hash (from_attributes), et TokenRead pour la future réponse de connexion (access_token, token_type, expires_in). extra="forbid" sur les entrées, comme les autres schémas.
- backend/app/repositories/user.py : ajoute get_by_email et add à UserRepository (aucun commit()).
- backend/app/core/exceptions.py : une exception « email déjà utilisé ». Ajoute-la à la table de correspondance de main.py pour qu'elle sorte en 409 (le gestionnaire cherche le type exact, une sous-classe absente de la table sortirait en 400).
- backend/app/services/auth.py : AuthService.register, qui lève cette exception si l'email est pris et hache le mot de passe avec hash_password avant l'ajout.
- backend/app/routers/auth.py : POST /auth/register, 201, response_model=UserRead. Inclus le router dans main.py.
- Tests pytest : inscription valide (201, ni password ni password_hash dans la réponse, condensat pbkdf2 en base), même email deux fois (409), email invalide, mot de passe de 4 et de 200 caractères (422, parametrize).

Ne protège encore aucune route (étape 4). Lance docker compose run --rm backend pytest. Ne touche pas au frontend. Pas de commentaires inutiles, ne fais pas de commit. Respecte .github/copilot-instructions.md pour le journal. Ajoute ce prompt tel quel à la fin de docs/tp/seance-5/prompts.md, sous le titre « Étape 2 : inscription ».
```
