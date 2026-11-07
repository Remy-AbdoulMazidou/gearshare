# Attaque temporelle sur le login (séance 5, « Pour aller plus loin »)

Mesures et vérifications faites par moi. Texte mis en forme avec l'aide de Claude. Code écrit par
GitHub Copilot (mode Agent), prompt à la fin de `prompts.md`.

## Le problème

Remarque de ma relecture finale : `authenticate` s'arrêtait sans hacher quand l'email n'existait
pas. Le message est le même (« Email ou mot de passe incorrect »), mais le temps de réponse
révélait si un compte existe.

## Mesures avec curl

Compte de test `temps@esiee.fr` créé, puis 5 connexions par cas :

```bash
curl -s -o /dev/null -w "%{time_total}s\n" -X POST http://localhost:8000/auth/login \
  -d "username=inconnu@esiee.fr&password=motdepasse-temps"
```

| Cas | Avant | Après |
|---|---|---|
| Email inconnu | 0,004 à 0,008 s (une mesure à 0,037 s) | 0,051 s (première mesure à 0,084 s) |
| Mauvais mot de passe | 0,051 à 0,066 s | 0,051 à 0,062 s |

Avant, l'email inconnu répondait environ 8 fois plus vite. Après, les deux cas coûtent un hachage
PBKDF2 complet, soit environ 0,05 s.

## La correction

```python
DUMMY_PASSWORD_HASH = hash_password(secrets.token_urlsafe())

def authenticate(self, email: str, password: str) -> User | None:
    user = self.repository.get_by_email(email)
    if user is None:
        verify_password(password, DUMMY_PASSWORD_HASH)
        return None
    ...
```

Le condensat factice est calculé une seule fois, au chargement du module. Il a le même format et
le même nombre d'itérations qu'un vrai, donc la vérification prend le même temps.

## Le test

Un test basé sur le chronomètre serait instable. Le test remplace `verify_password` par un espion
qui compte les appels, envoie un login avec un email inconnu, et vérifie le 401 et un appel
exactement.

Mutation : ligne `verify_password(password, DUMMY_PASSWORD_HASH)` supprimée, le test échoue
(`1 failed, 104 passed`). Ligne remise : `105 passed`.

## Limite restante

L'inscription révèle toujours si un email existe : elle répond 409 « Cette adresse email est déjà
utilisée ». Je la garde, car l'utilisateur doit comprendre pourquoi son inscription échoue. La
supprimer demanderait une confirmation par email, hors du périmètre du projet.
