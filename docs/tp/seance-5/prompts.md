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

## Étape 3 : connexion et JWT

```text
Étape 3 du TP ../cours/seances/seance-5-authentification/tp/README.md, en suivant le cours ../cours/seances/seance-5-authentification/cours/README.md.

- backend/app/core/security.py : create_access_token et decode_access_token avec PyJWT. HS256, settings.jwt_secret, sub sous forme de chaîne, iat et exp (settings.jwt_expire_minutes), et rien d'autre dans le payload. Au décodage, liste explicite d'algorithmes (["HS256"]) et exp vérifié.
- AuthService.authenticate(email, password) : renvoie l'utilisateur ou None. Même résultat pour un email inconnu et un mauvais mot de passe.
- POST /auth/login : lit un formulaire OAuth2PasswordRequestForm (username porte l'email), renvoie TokenRead (access_token, token_type "bearer", expires_in en secondes), ou un 401 avec l'en-tête WWW-Authenticate: Bearer et le même message dans les deux cas d'échec.
- Tests : connexion réussie (jeton décodable, sub = id de l'utilisateur), et un test paramétré qui vérifie que mauvais mot de passe et email inexistant donnent le même 401, le même corps et l'en-tête WWW-Authenticate.

Ne protège encore aucune route (étape 4). Lance docker compose run --rm backend pytest. Ne touche pas au frontend. Pas de commentaires inutiles, ne fais pas de commit. Respecte .github/copilot-instructions.md pour le journal. Ajoute ce prompt tel quel à la fin de docs/tp/seance-5/prompts.md, sous le titre « Étape 3 : connexion et JWT ».
```

## Étape 4 : get_current_user et routes protégées

```text
Étape 4 du TP ../cours/seances/seance-5-authentification/tp/README.md, en suivant le cours ../cours/seances/seance-5-authentification/cours/README.md.

- backend/app/api/deps.py : get_current_user avec OAuth2PasswordBearer(tokenUrl="/auth/login"), qui réutilise decode_access_token (sans réécrire jwt.decode) et relit l'utilisateur en base par UserRepository. Quelle que soit la cause (pas de jeton, jeton malformé, expiré, utilisateur disparu), le même 401 avec WWW-Authenticate: Bearer. Ajoute l'alias CurrentUser.
- GET /auth/me, authentifié, response_model=UserRead.
- Protection : GET /items et GET /items/{id} restent publiques. POST /items authentifié, le propriétaire vient du jeton. PUT, PATCH et DELETE /items/{id} authentifiés (la vérification de propriété sera faite à l'étape 5, ne l'ajoute pas encore). Toutes les routes /reservations authentifiées, l'emprunteur vient du jeton.
- Retire owner_id de ItemCreate et ItemUpdate, et borrower_id de ReservationCreate. Les services reçoivent l'utilisateur connecté.
- Tests : adapte les fixtures pour que les tests existants s'exécutent avec un client authentifié, sans changer leurs assertions sauf ce qu'impose la disparition de owner_id et borrower_id. Ajoute les tests de GET /auth/me (200 avec jeton, 401 sans jeton et avec un jeton bidon). Liste dans le journal chaque test modifié et pourquoi.

Ne touche pas au frontend (étape 7). Lance docker compose run --rm backend pytest. Pas de commentaires inutiles, ne fais pas de commit. Respecte .github/copilot-instructions.md pour le journal. Ajoute ce prompt tel quel à la fin de docs/tp/seance-5/prompts.md, sous le titre « Étape 4 : get_current_user et routes protégées ».
```

## Étape 5 : propriété et 403

```text
Étape 5 du TP ../cours/seances/seance-5-authentification/tp/README.md, en suivant le cours ../cours/seances/seance-5-authentification/cours/README.md.

Aujourd'hui, Bob peut supprimer l'item d'Alice (DELETE /items/{id} renvoie 204). Ajoute la vérification de propriété dans les services, avec l'exception métier AccesRefuse de la séance 4 (déjà traduite en 403 par le gestionnaire global) :
- ItemService : remplacer, modifier et supprimer un item seulement si l'utilisateur connecté en est le propriétaire, sinon AccesRefuse.
- ReservationService : annuler une réservation seulement si l'utilisateur connecté est l'emprunteur ou le propriétaire de l'item, sinon AccesRefuse. Garde l'ordre : 404 si la réservation n'existe pas, puis 403, puis 409 si elle n'est pas active.
- Aucune vérification dans les routers.
- Tests : Bob qui supprime, remplace ou modifie l'item d'Alice reçoit 403 et l'item est inchangé. Un tiers qui annule une réservation reçoit 403, l'emprunteur et le propriétaire de l'item peuvent annuler. Un test du service sans HTTP qui vérifie que supprimer l'item d'un autre lève AccesRefuse.

Lance docker compose run --rm backend pytest. Ne touche pas au frontend. Pas de commentaires inutiles, ne fais pas de commit. Respecte .github/copilot-instructions.md pour le journal. Ajoute ce prompt tel quel à la fin de docs/tp/seance-5/prompts.md, sous le titre « Étape 5 : propriété et 403 ».
```

## Étape 6 : tests de la matrice

```text
Étape 6 du TP ../cours/seances/seance-5-authentification/tp/README.md, en suivant le cours ../cours/seances/seance-5-authentification/cours/README.md.

- conftest.py : une fixture bob sur le modèle d'alice, et deux fixtures client_alice et client_bob qui sont des instances distinctes de TestClient, chacune avec son propre jeton dans ses en-têtes. Ne modifie plus le jeton d'un client partagé dans les tests : remplace ce mécanisme par ces fixtures.
- Pour chaque ligne de la matrice (POST /items, PUT/PATCH/DELETE /items/{id}, POST /reservations, annulation d'une réservation, GET /auth/me), trois tests : anonyme (401), propriétaire (succès), autre utilisateur (403, ou succès quand la règle l'autorise). Utilise parametrize quand c'est lisible.
- Un test qui envoie l'owner_id de Bob dans le corps de POST /items avec le jeton d'Alice. Comme ItemCreate a extra="forbid", vérifie le 422 sur le champ owner_id et qu'aucun item n'a été créé pour Bob.
- Garde le test paramétré du login (mauvais mot de passe et email inexistant, même 401 et même corps) et le test du service qui vérifie AccesRefuse sur la suppression de l'item d'un autre. Ne duplique pas ce qui existe déjà.

Lance docker compose run --rm backend pytest -v. Ne touche pas au frontend. Pas de commentaires inutiles, ne fais pas de commit. Respecte .github/copilot-instructions.md pour le journal. Ajoute ce prompt tel quel à la fin de docs/tp/seance-5/prompts.md, sous le titre « Étape 6 : tests de la matrice ».
```
