# Prompts de la séance 5

## Étape 1 : hachage des mots de passe

```text
Étape 1 du TP ../cours/seances/seance-5-authentification/tp/README.md, en suivant le cours ../cours/seances/seance-5-authentification/cours/README.md.

- backend/app/core/security.py : hash_password et verify_password. PBKDF2-HMAC-SHA256 de hashlib, 600 000 itérations, sel de 16 octets tiré avec secrets. Condensat auto-descriptif dans une seule chaîne (algorithme, nombre d'itérations, sel, condensat). verify_password relit le nombre d'itérations dans la chaîne stockée, compare en temps constant avec hmac.compare_digest, et renvoie False sans lever d'exception sur un condensat malformé.
- backend/tests/test_security.py, sans base ni client HTTP : deux hachages du même mot de passe sont différents, le bon mot de passe est accepté et un mauvais refusé, un condensat malformé ("x") est refusé sans erreur, un condensat produit avec un autre nombre d'itérations reste vérifiable.

Lance docker compose run --rm backend pytest tests/test_security.py -v, puis toute la suite. Ne touche ni aux routers ni au frontend. Pas de commentaires inutiles, ne fais pas de commit. Respecte .github/copilot-instructions.md pour le journal. Ajoute ce prompt tel quel à la fin de docs/tp/seance-5/prompts.md (crée le fichier avec un titre « Prompts de la séance 5 »), sous le titre « Étape 1 : hachage des mots de passe ».
```
