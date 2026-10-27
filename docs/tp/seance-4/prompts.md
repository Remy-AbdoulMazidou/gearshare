# Prompts de la séance 4

## TP 1, étape 1 : squelette du frontend

Outil : GitHub Copilot, mode Agent, dans VS Code. Copilot a lu le TP et le cours, proposé un plan
que j'ai validé, puis créé les fichiers et vérifié le démarrage avec Docker.

```text
Étape 1 du TP ../cours/seances/seance-4-webapp/tp/tp1-frontend.md : crée le squelette du frontend en suivant le cours ../cours/seances/seance-4-webapp/cours/cours1-frontend.md (sections 2.2, 2.4, 2.6 et 2.8).

- frontend/requirements.txt : fastapi, uvicorn[standard] et httpx aux mêmes versions que backend/requirements.txt, plus jinja2==3.1.4 et python-multipart==0.0.9.
- frontend/Dockerfile : reprends backend/Dockerfile sans les tests, avec le port 8080.
- Ajoute un service frontend dans docker-compose.yml : build ./frontend, API_BASE_URL=http://backend:8000 dans environment, depends_on backend, port 8080, volume ./frontend/app, uvicorn avec --reload comme le backend.
- frontend/app : __init__.py, routers/__init__.py, templating.py, main.py (monte /static, GET / redirige vers /items), templates/base.html (section 2.4), templates/erreur.html (étend base.html, affiche {{ message }} dans un paragraphe avec un lien de retour vers /items), static/style.css (copie de la section 2.8).

Ne crée pas encore api_client.py, routers/items.py ni les templates items : ce sont les étapes suivantes. Pas de commentaires inutiles, ne touche pas au backend, ne fais pas de commit.
```

Remarque : Copilot a aussi mis à jour `SUIVI.md` et `journal.md`, en suivant les règles de
`CLAUDE.md`. Il a écrit « Claude Code » dans le journal et oublié les étapes 5 et 6 de la
séance 3. J'ai corrigé ces deux fichiers à la main.

## TP 1, étape 2 : client d'API

Outil : GitHub Copilot, mode Agent, dans VS Code.

```text
Étape 2 du TP ../cours/seances/seance-4-webapp/tp/tp1-frontend.md : écris frontend/app/api_client.py en partant de la section 2.5 du cours ../cours/seances/seance-4-webapp/cours/cours1-frontend.md.

- Classe ApiClient avec seulement list_items, get_item et create_item (pas encore les réservations), et l'instance unique api_client en fin de module.
- Ajoute à ApiError une méthode messages() qui renvoie une liste de messages affichables : si detail est une chaîne, une liste avec cette chaîne ; si c'est une liste d'erreurs 422 de FastAPI, un message par erreur sous la forme "nom du champ : msg", le nom du champ étant le dernier élément de loc.
- Dans frontend/app/main.py, ajoute le gestionnaire d'exceptions ApiError de la section 2.6.

Pas de commentaires inutiles, ne touche pas au backend, ne fais pas de commit.


## TP 1, étape 3 : pages liste et détail

Outil : GitHub Copilot, mode Agent.

```text
Étape 3 du TP ../cours/seances/seance-4-webapp/tp/tp1-frontend.md, en suivant les sections 2.4 et 2.6 du cours ../cours/seances/seance-4-webapp/cours/cours1-frontend.md.

- frontend/app/routers/items.py : routes GET /items et GET /items/{item_id}, qui passent uniquement par api_client. Inclus le router dans main.py.
- templates/items/list.html : le tableau du cours, avec au-dessus un lien « Proposer un objet » vers /items/new.
- templates/items/detail.html : titre, description, tarif, statut et un lien de retour vers la liste.

Pas de |safe, pas de JavaScript, pas de commentaires inutiles. Ne touche pas au backend, ne fais pas de commit. Respecte .github/copilot-instructions.md pour le journal.
```

## TP 1, étape 4 : formulaire de création

Outil : GitHub Copilot, mode Agent.

```text
Étape 4 du TP ../cours/seances/seance-4-webapp/tp/tp1-frontend.md, en appliquant le schéma Post/Redirect/Get de la section 2.7 du cours ../cours/seances/seance-4-webapp/cours/cours1-frontend.md à la création d'un item.

- Dans frontend/app/routers/items.py : GET /items/new qui affiche templates/items/form.html, déclarée avant GET /items/{item_id}. POST /items qui lit les quatre champs avec Form(), appelle api_client.create_item, puis redirige en 303 vers la page de détail du nouvel item.
- disponible a False comme valeur par défaut (une case non cochée n'envoie rien). Une description vide est envoyée au backend comme None.
- En cas d'ApiError 422 : réaffiche le formulaire avec le code 422, les messages de exc.messages() au-dessus du formulaire et les valeurs saisies. Toute autre erreur remonte au gestionnaire global.
- form.html : titre (required minlength="3"), description (textarea), tarif_jour (number, required min="0.01" step="0.01"), disponible (checkbox), chaque champ prérempli avec la saisie précédente.

Pas de |safe, pas de JavaScript, pas de commentaires inutiles. Ne touche pas au backend, ne fais pas de commit. Respecte .github/copilot-instructions.md pour le journal.
```



## TP 1, étape 5 : réserver et annuler

Outil : GitHub Copilot, mode Agent. Deux prompts : d'abord le backend, puis le frontend.

### Partie A : backend

Le TP impose `PATCH /reservations/{id}`, alors que mon API avait `POST /reservations/{id}/annuler`.
Comme les tests de la séance 2 doivent passer sans modification, j'ai choisi d'ajouter `PATCH` en
gardant l'ancienne route, avec une logique commune.

```text
Étape 5 du TP ../cours/seances/seance-4-webapp/tp/tp1-frontend.md : le frontend annulera une réservation avec PATCH /reservations/{reservation_id} et le corps {"statut": "annulee"}. Prépare le backend (backend/app/routers/reservations.py et backend/app/schemas/reservation.py) :

- Ajoute PATCH /reservations/{reservation_id} avec un schéma ReservationUpdate (extra="forbid", statut: Literal["annulee"]). Même comportement que POST /reservations/{reservation_id}/annuler : 404 si la réservation n'existe pas, 409 si elle est déjà annulée, envoi de la notification. Factorise la logique commune au lieu de la dupliquer.
- Garde POST /reservations/{reservation_id}/annuler : les tests de la séance 2 doivent passer sans modification.
- Vérifie que GET /reservations accepte un filtre item_id. Ajoute-le seulement s'il manque.
- Ajoute des tests pytest pour PATCH dans backend/tests/test_reservations.py, sans modifier les tests existants : succès, 404, 409, et 422 si statut vaut autre chose que "annulee".

Lance docker compose run --rm backend pytest. Pas de commentaires inutiles, ne touche pas au frontend, ne fais pas de commit. Respecte .github/copilot-instructions.md pour le journal.
```

Résultat : 52 tests verts. Copilot avait réécrit une décision du 24/09 dans `SUIVI.md`, je l'ai
remise et j'ai ajouté une nouvelle décision datée du 22/10.

### Partie B : frontend

```text
Étape 5 du TP ../cours/seances/seance-4-webapp/tp/tp1-frontend.md, partie frontend, en suivant les sections 2.5 et 2.7 du cours ../cours/seances/seance-4-webapp/cours/cours1-frontend.md. Le backend expose déjà GET /reservations?item_id=..., POST /reservations et PATCH /reservations/{reservation_id} (404, et 409 si déjà annulée).

- api_client.py : ajoute list_reservations(item_id), create_reservation(item_id, date_debut, date_fin) et update_reservation_statut(reservation_id, statut).
- Nouveau router frontend/app/routers/reservations.py, inclus dans main.py :
  - POST /items/{item_id}/reservations : appelle create_reservation puis redirige en 303 vers /items/{item_id}?reservation=ok. En cas de 409 ou 422, réaffiche detail.html avec le même code, les messages de exc.messages() et les dates saisies. Les autres erreurs remontent au gestionnaire global.
  - POST /reservations/{reservation_id} : lit les champs cachés statut et item_id, appelle update_reservation_statut puis redirige en 303 vers /items/{item_id}. Si le backend répond 409, redirige en 303 vers /items/{item_id}?annulation=deja.
- GET /items/{item_id} charge aussi les réservations de l'item.
- detail.html : liste des réservations (dates et statut), pour chaque réservation active un formulaire POST « Annuler » avec les champs cachés statut=annulee et item_id, le formulaire « Réserver » avec deux champs date obligatoires, le message « Votre réservation est enregistrée. », les messages d'erreur, et « Cette réservation est déjà annulée. » quand annulation=deja.

Contraintes du TP : aucun httpx en dehors de api_client.py, aucune vérification de dates en Python, pas de JavaScript, pas de |safe, aucune adresse de backend en dur. Pas de commentaires inutiles, ne touche pas au backend, ne fais pas de commit. Respecte .github/copilot-instructions.md pour le journal.

Contraintes du TP : aucun httpx en dehors de api_client.py, aucune vérification de dates en Python, pas de JavaScript, pas de |safe, aucune adresse de backend en dur. Pas de commentaires inutiles, ne touche pas au backend, ne fais pas de commit. Respecte .github/copilot-instructions.md pour le journal.
```

Ensuite, correction de `ApiError.messages()` par moi : le message affichait
« body : Value error, date_fin doit être postérieure à date_debut ».


## TP 2, étape 1 : configuration et session

Outil : GitHub Copilot, mode Agent.

```text
Étape 1 du TP ../cours/seances/seance-4-webapp/tp/tp2-backend-db.md, en suivant les sections 2.1, 3 et 7 du cours ../cours/seances/seance-4-webapp/cours/cours2-backend-db.md.

- backend/app/core/config.py : classe Settings (pydantic-settings) avec database_url obligatoire et sql_echo à False par défaut, instance settings créée une seule fois au niveau du module.
- backend/app/db/session.py : engine SQLAlchemy construit depuis settings, avec pool_pre_ping=True et echo=settings.sql_echo, et la fabrique SessionLocal.
- backend/app/api/deps.py : get_db qui ouvre une session par requête, commit si tout s'est bien passé, rollback en cas d'exception, close dans tous les cas. Ajoute l'alias DbSession.
- .env.example à la racine du dépôt : POSTGRES_USER=gearshare, POSTGRES_PASSWORD=gearshare, POSTGRES_DB=gearshare, DATABASE_URL au format postgresql+psycopg://utilisateur:motdepasse@hote:port/base, SQL_ECHO=false.

Ne branche rien dans main.py ni dans les routers, ce sont les étapes suivantes. Ne touche pas au frontend. Pas de commentaires inutiles, ne fais pas de commit. Respecte .github/copilot-instructions.md pour le journal.
```

## TP 2, étape 2 : les modèles

```text
Étape 2 du TP ../cours/seances/seance-4-webapp/tp/tp2-backend-db.md, en suivant les sections 2.2 et 2.3 du cours ../cours/seances/seance-4-webapp/cours/cours2-backend-db.md.

Écris backend/app/models/base.py, user.py, item.py et reservation.py en traduisant exactement les tables users, items et reservations de tp-db/sql/init/01-schema.sql (pas 03-schema-v2.sql) :
- index=True sur toutes les clés étrangères, avec le même ondelete que le SQL ;
- Numeric(8, 2) pour tarif_jour ;
- DateTime(timezone=True) avec server_default=func.now() pour created_at ;
- User.email unique ;
- les CHECK dans __table_args__, nommés : tarif positif, dates_coherentes, statut_valide ;
- relationship(back_populates=...) des deux côtés de chaque lien.
backend/app/models/__init__.py importe Base et les trois modèles.

Ne touche ni aux routers, ni à main.py, ni au frontend. Pas de commentaires inutiles, ne fais pas de commit. Respecte .github/copilot-instructions.md pour le journal. Ajoute ce prompt tel quel à la fin de docs/tp/seance-4/prompts.md, sous le titre « TP 2, étape 2 : les modèles ».
```

## TP 2, étape 3 : brancher Alembic

```text
Étape 3 du TP ../cours/seances/seance-4-webapp/tp/tp2-backend-db.md, en suivant la section 6 et la section 8 du cours ../cours/seances/seance-4-webapp/cours/cours2-backend-db.md. J'ai déjà lancé alembic init alembic dans backend/.

- backend/alembic/env.py : l'URL de connexion vient de settings.database_url (app.core.config), pas de alembic.ini. target_metadata = Base.metadata, avec les modèles importés via app.models.
- backend/alembic.ini : laisse sqlalchemy.url vide.
- backend/Dockerfile : copie aussi alembic/ et alembic.ini dans l'image.
- docker-compose.yml : ajoute un service db (postgres:16, identifiants par substitution depuis le .env, volume nommé, healthcheck pg_isready, pas de port publié). Le service backend reçoit env_file: .env, dépend de db avec condition service_healthy, et monte aussi ./backend/alembic et ./backend/alembic.ini. Le frontend ne change pas.

Ne génère pas de migration : je la lance et je la relis moi-même. N'ajoute pas encore l'application automatique des migrations au démarrage (étape 6). Ne touche ni aux routers, ni à main.py, ni au frontend. Pas de commentaires inutiles, ne fais pas de commit. Respecte .github/copilot-instructions.md pour le journal. Ajoute ce prompt tel quel à la fin de docs/tp/seance-4/prompts.md, sous le titre « TP 2, étape 3 : brancher Alembic ».
```

## TP 2, étape 4 : verticale items

```text
Étape 4 du TP ../cours/seances/seance-4-webapp/tp/tp2-backend-db.md, en suivant les sections 1, 4 et 5 du cours ../cours/seances/seance-4-webapp/cours/cours2-backend-db.md. Écris la ressource items couche par couche, dans cet ordre, en vérifiant chaque fichier avant de passer au suivant :

1. backend/app/core/exceptions.py : une exception métier de base et trois sous-classes (introuvable, conflit, accès refusé), avec un message lisible. Aucune ne connaît HTTP.
2. backend/app/schemas/item.py : ItemCreate (ajoute owner_id), ItemUpdate (tous les champs optionnels), ItemRead construit depuis l'objet SQLAlchemy (from_attributes), avec owner_id. Garde extra="forbid" et les validations existantes.
3. backend/app/repositories/item.py : ItemRepository (get, list avec skip/limit, recherche q sur le titre et filtre disponible, add, delete). Aucun commit().
4. backend/app/services/item.py : ItemService, qui lève l'exception « introuvable » si l'item n'existe pas. Pas d'autre règle métier.
5. backend/app/routers/items.py : garde exactement le contrat de la séance 1 (mêmes routes, y compris PUT, mêmes paramètres et mêmes codes de statut). Le router ne fait que traduire : schéma en entrée, appel au service, schéma en sortie. Plus de FAKE_DB pour items.

Dans backend/app/main.py : garde /health et le router reservations tel quel (il reste en mémoire jusqu'à l'étape 7), et traduis les exceptions métier en codes HTTP (404, 409, 403) avec un gestionnaire d'exceptions global, qui renvoie {"detail": message}.

Ne modifie pas les tests : je les remettrai au vert sur une base de test à l'étape suivante. Ne touche pas au frontend. Pas de commentaires inutiles, ne fais pas de commit. Respecte .github/copilot-instructions.md pour le journal. Ajoute ce prompt tel quel à la fin de docs/tp/seance-4/prompts.md, sous le titre « TP 2, étape 4 : verticale items ».
```

## TP 2, étape 4 : propriétaire inexistant

```text
Suite de l'étape 4 du TP ../cours/seances/seance-4-webapp/tp/tp2-backend-db.md (point de contrôle). Aujourd'hui, POST /items avec un owner_id inexistant renvoie 500 : c'est l'IntegrityError de PostgreSQL qui remonte. Le client doit recevoir un 404 clair, détecté par le service avant l'écriture.

- Crée backend/app/repositories/user.py avec un UserRepository qui sait récupérer un utilisateur par id (même style que ItemRepository, aucun commit()).
- Dans ItemService, avant de créer ou de remplacer un item, et avant de modifier son owner_id si ItemUpdate le permet, vérifie que le propriétaire existe. Sinon, lève RessourceIntrouvable avec le message "Utilisateur {id} introuvable".
- Adapte l'injection dans le router si nécessaire, sans mettre de logique dans le router.

Ne modifie pas les tests, ne touche pas au frontend. Pas de commentaires inutiles, ne fais pas de commit. Respecte .github/copilot-instructions.md pour le journal. Ajoute ce prompt tel quel à la fin de docs/tp/seance-4/prompts.md, sous le titre « TP 2, étape 4 : propriétaire inexistant ».
```

## TP 2 : tests sur une base PostgreSQL de test

Remets la suite de tests du backend au vert en suivant les sections 9.1 et 9.2 du cours ../cours/seances/seance-4-webapp/cours/cours2-backend-db.md (option A, PostgreSQL de test). La base gearshare_test existe déjà dans le service db.

- Ajoute test_database_url (str | None = None) à Settings, et TEST_DATABASE_URL dans .env.example (même serveur, base gearshare_test). J'ajouterai la ligne à mon .env moi-même.
- backend/tests/conftest.py : fixtures engine (scope session, create_all/drop_all), db (transaction annulée à la fin de chaque test), client (dependency_overrides sur get_db), et une fixture alice (utilisateur inséré par flush). La fixture item_velo crée l'item avec owner_id=alice.id. Les réservations sont encore en mémoire jusqu'à l'étape 7 : garde la remise à zéro de leur FAKE_DB.
- Les tests d'items de la séance 2 doivent changer le moins possible. La seule différence de contrat est owner_id, désormais obligatoire dans ItemCreate : ajoute-le là où c'est nécessaire et ne change pas les assertions. Liste dans le journal chaque test modifié et pourquoi.
- Ajoute un test pour le cas owner_id inexistant (404 « Utilisateur 999 introuvable »).

Lance docker compose run --rm backend pytest. Ne touche pas au frontend. Pas de commentaires inutiles, ne fais pas de commit. Respecte .github/copilot-instructions.md pour le journal. Ajoute ce prompt tel quel à la fin de docs/tp/seance-4/prompts.md, sous le titre « TP 2 : tests sur une base PostgreSQL de test ».
