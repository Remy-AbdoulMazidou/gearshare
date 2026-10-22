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
