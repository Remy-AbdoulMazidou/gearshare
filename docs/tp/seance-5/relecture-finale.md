# Relecture finale de la séance 5 (étape 9)

Relecture faite par moi avec la liste du prof, en vérifiant chaque point dans le code et avec les
expériences de l'étape 8. Texte mis en forme avec l'aide de Claude.

## Liste de contrôle

| Point | État | Où je l'ai vérifié |
|---|---|---|
| `JWT_SECRET` hors du code, 32 octets aléatoires ou plus | OK | `.env` (généré avec `openssl rand -hex 32`), `.env.example` ne contient qu'une valeur factice, `jwt_secret` sans valeur par défaut dans `Settings` |
| `.env` absent du dépôt et de l'historique Git | OK | `git log --all --oneline -- .env` n'affiche rien |
| Le frontend ne reçoit pas `JWT_SECRET` | OK | `docker compose exec frontend env \| grep -i jwt` n'affiche rien |
| Hachage PBKDF2-HMAC-SHA256, 600 000 itérations, sel tiré par `secrets` | OK | `backend/app/core/security.py`, 0,050 s par hachage mesuré |
| Comparaison des condensats en temps constant | OK | `hmac.compare_digest` dans `verify_password` |
| `password_hash` absent de tous les schémas de lecture | OK | `UserRead` et `OwnerRead`, réponse d'inscription relue |
| Payload du JWT limité à `sub`, `iat`, `exp` | OK | Payload lu sans clé à l'étape 3 |
| `exp` présent et vérifié | OK | Étape 8.2 : 200 puis 401 après expiration |
| Liste explicite d'algorithmes au décodage | OK | `algorithms=["HS256"]` dans `decode_access_token` |
| `get_current_user` relit l'utilisateur en base | OK | Étape 8.3 : compte supprimé, ancien jeton refusé (401) |
| Même `401` quelle que soit la cause, avec `WWW-Authenticate` | OK | Sans jeton, jeton bidon, expiré, utilisateur supprimé : « Authentification invalide » |
| Toutes les routes d'écriture protégées | OK | Matrice de tests (étape 6) et expérience de la route `DELETE` non protégée : 2 tests échouent |
| L'identité vient du jeton, jamais du corps | OK | `owner_id` et `borrower_id` retirés des schémas, `extra="forbid"` refuse un `owner_id` envoyé (422) |
| Propriété vérifiée dans le service, `403` renvoyé | OK | `ItemService` et `ReservationService`, Bob reçoit 403 sur l'item d'Alice |
| Message de login identique pour un email inconnu et un mauvais mot de passe | OK | « Email ou mot de passe incorrect », test paramétré |
| Longueur minimale et maximale du mot de passe | OK | 12 à 128 caractères, 422 sur 4 et 200 caractères |
| Aucun mot de passe dans les logs | OK | Seul `services/reservation.py` journalise, avec l'id de la réservation |
| Jeton passé en paramètre au client d'API, jamais stocké dans l'instance | OK | Paramètre `token` de chaque méthode de `ApiClient` |
| Cookie `HttpOnly`, `SameSite=Lax`, `Secure` configurable | OK | Vu dans les outils du navigateur, `COOKIE_SECURE` dans `docker-compose.yml` |
| Aucune modification par `GET` dans le frontend, déconnexion comprise | OK | `/deconnexion` en `POST`, annulation et réservation en `POST` |
| Paramètre `suivant` limité aux pages du site | OK | `chemin_local` refuse ce qui ne commence pas par un seul `/`, testé avec `suivant=https://example.com` |

## Recherche de secrets oubliés

```bash
git grep -niE "secret|password|token" -- '*.py' '*.yml' '*.yaml' | grep -v "settings\.\|password_hash\|hash_password\|verify_password"
git log --all --oneline -- .env
```

La seconde commande n'affiche rien. La première affiche des lignes, toutes expliquées :

- noms de variables, de paramètres et de classes (`token`, `password`, `TokenRead`,
  `OAuth2PasswordBearer`, `access_token`) : aucune valeur secrète ;
- `import secrets` et `secrets.token_bytes` : tirage du sel ;
- `jwt_secret: str` dans `config.py` : déclaration du champ, la valeur vient de l'environnement ;
- mots de passe dans `backend/tests/` (`motdepasse-alice`, `1234`...) : comptes fictifs créés
  dans la base de test ;
- `POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}` dans `docker-compose.yml` : substitution depuis le
  `.env` ;
- `POSTGRES_PASSWORD: gearshare` dans `tp-db/docker-compose.yml` : base locale du TP de la
  séance 3, valeur de développement donnée par le TP, jamais utilisée par l'application.

## Remarques

- Les réponses 422 de FastAPI renvoient la valeur saisie dans `input`, mot de passe compris. Elle
  ne repart que vers celui qui l'a tapée, mais ces corps d'erreur ne doivent jamais être
  journalisés.
- `authenticate` répond plus vite pour un email inconnu (pas de hachage) que pour un mauvais mot de
  passe. Le message est identique, mais le temps de réponse peut révéler si un compte existe.
  Correction possible (« Pour aller plus loin ») : hacher un mot de passe factice quand
  l'utilisateur n'existe pas.
