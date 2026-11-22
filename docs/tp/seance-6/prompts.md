# Prompts de la séance 6

Prompts donnés à GitHub Copilot (mode Agent), copiés tels quels. Préparés avec l'aide de Claude.

## Étape 0 : AGENTS.md

```text
Contexte : séance 6, TP étape 0 (../cours/seances/seance-6-dev-agentic/tp/README.md). Il faut un AGENTS.md à la racine, source de vérité pour tous les agents, une soixantaine de lignes au plus.

1. Crée AGENTS.md à partir de CLAUDE.md et .github/copilot-instructions.md, en gardant seulement ce qui sert à chaque tâche :
   - stack et arborescence (backend/app : routers, schemas, services, repositories, models, core, api, db ; backend/alembic ; backend/tests ; frontend/app) ;
   - commandes : démarrer (docker compose up), tests (docker compose run --rm backend pytest), lint (la commande docker de la section Qualité du README), créer une migration (alembic revision --autogenerate dans le conteneur backend) et l'appliquer (docker compose run --rm migrate) ;
   - conventions : logique métier dans les services, routers sans accès aux données, validation dans Pydantic, codes HTTP (201, 204, 401, 403, 404, 409, 422, jamais de 500 volontaire), erreurs métier traduites par le gestionnaire de main.py, nommage des tests test_ac_<story>_<critère>_..., une migration autogenerate est toujours relue ;
   - interdits : aucun secret dans le code, ne jamais modifier une migration déjà appliquée, identité toujours tirée du jeton et jamais du corps de la requête, ne jamais lancer git commit ni git push ;
   - traces : prompts copiés tels quels dans prompts.md, l'agent se nomme dans docs/suivi/journal.md et ne note que des vérifications réellement réussies, SUIVI.md et journal.md mis à jour à la fin d'une tâche, les fichiers de review et docs/retour-experience.md sont écrits par Rémy.

2. Remplace tout le contenu de CLAUDE.md par la seule ligne @AGENTS.md.

3. Supprime .github/copilot-instructions.md : son contenu est fusionné dans AGENTS.md.

4. Crée docs/tp/seance-6/prompts.md (titre « Prompts de la séance 6 », puis une première ligne : « Prompts donnés à GitHub Copilot (mode Agent), copiés tels quels. Préparés avec l'aide de Claude. »), et ajoute ce prompt dans un bloc de code sous « Étape 0 : AGENTS.md ».

Français simple, pas de commentaire inutile, pas de lignes vides en trop. Donne-moi le nombre de lignes final d'AGENTS.md. Pas de commit.
```
