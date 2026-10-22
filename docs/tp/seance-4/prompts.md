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
```

Ensuite, correction de `ApiError.messages()` par moi : le message affichait
« body : Value error, date_fin doit être postérieure à date_debut ».
