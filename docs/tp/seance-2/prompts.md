Rédigé avec Claude Code, relu et corrigé par Rémy.

# Prompts utilisés pour le TP séance 2

Agent : Claude Code.
Prompts préparés avec Claude (chat), puis exécutés par Claude Code dans le dépôt.

## Prompt 1

TP 2, étape 1. Lis d'abord ../cours/seances/seance-2-tests/cours/README.md (sections 2 et 3.4) et le projet-demo de ../cours/seances/seance-2-tests/tp/projet-demo/.

Objectif : pouvoir lancer pytest dans le conteneur, et supprimer les compteurs globaux.
1. Ajoute pytest, pytest-cov et httpx à requirements.txt, avec les mêmes versions que le projet-demo du prof.
2. Ajoute pytest.ini et tests/test_health.py comme dans le projet-demo.
3. Adapte le Dockerfile et le docker-compose.yml pour que tests/ et pytest.ini soient dans le conteneur et que mes modifications de tests soient prises en compte sans rebuild.
4. Supprime la variable globale _next_id dans les deux routers et remplace-la par une fonction _next_id() calculée depuis FAKE_DB, comme dans la section 3.4 du cours.

Avant tout, copie ce message tel quel dans docs/tp/seance-2/prompts.md sous un titre « Prompt 1 ».
Propose ton plan avant de coder. Termine par « À savoir expliquer » et un message de commit. Ne commite pas.
