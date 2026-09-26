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

## Prompt 2

TP 2, étape 2. Lis les sections 3, 4 et 5 du cours de la séance 2.

1. tests/conftest.py : dataclass Storage (items, reservations) avec reset_all(), fixture storage (remise à zéro avant et après), fixture client qui dépend de storage, fixture item_velo. Exactement le montage des sections 3.4 et 3.5, sans autouse.
2. Adapte test_health.py pour qu'il utilise la fixture client.
3. tests/test_items.py, qui couvre la grille de la section 5 pour items :
   - création nominale ;
   - validation 422 en parametrize, en vérifiant le champ en erreur avec loc[-1] (section 4.3) ;
   - 404 sur GET, PUT, PATCH et DELETE ;
   - PATCH partiel qui conserve les autres champs ;
   - DELETE puis GET qui renvoie 404 ;
   - filtres q et disponible ;
   - pagination skip/limit, avec storage pour préparer les données.
Un test par cas, noms en français explicites, Given/When/Then quand ce n'est pas évident. Pour chaque raise du router, un test.

Copie ce message tel quel dans docs/tp/seance-2/prompts.md sous « Prompt 2 ».
Propose ton plan avant de coder, avec la liste des noms de tests. Lance pytest à la fin. Termine par « À savoir expliquer » et un message de commit. Ne commite pas.
