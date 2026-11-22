# Plan d’implémentation — Avis

Rédigé avec GitHub Copilot (mode Plan) en suivant .github/agents/planificateur.agent.md, relu et corrigé par Rémy.

**Fiche** : [fiche.md](fiche.md)
**Statut** : validé

## 1. Rappel du périmètre

- User stories couvertes : US-01, US-02, US-03.
- MVP :
  - clôture explicite d’une réservation active par le propriétaire ;
  - publication d’un avis entier de 1 à 5 avec commentaire optionnel limité à 500 caractères ;
  - interdiction des avis multiples sur une réservation ;
  - moyenne d’une décimale et nombre d’avis sur la page de détail ;
  - interface propriétaire/emprunteur pour les actions métier.
- Hors plan :
  - modifications ou suppressions d’avis ;
  - notation de l’emprunteur ;
  - modération, réponses aux avis et notifications ;
  - réputation sur la liste des annonces ;
  - historique détaillé du prêteur ;
  - délai ou fenêtre de publication.

## 2. Décisions retenues

- Routes API proposées :
  - `POST /reservations/{reservation_id}/cloturer`
  - `POST /reservations/{reservation_id}/avis`
- La clôture reste une action indépendante de l’annulation actuelle.
- Le modèle `Avis` relie un avis à sa réservation.
  - La réservation fournit l’emprunteur et le matériel.
  - Une contrainte unique sur `reservation_id` garantit qu’il n’existe qu’un avis par réservation.
- Champs de l’avis :
  - `note` : entier SQL compris entre 1 et 5 ;
  - `commentaire` : texte nullable de 500 caractères maximum ;
  - `created_at` : horodatage optionnel pour les besoins futurs.
- Les champs de réputation exposés sur le détail d’une annonce seront :
  - `reputation_moyenne : float | None`
  - `reputation_nombre : int`
  - `Aucun avis` est produit par le frontend lorsque `reputation_nombre == 0`.
- La moyenne est calculée dynamiquement par le backend.
  - Arrondi classique à une décimale avec `Decimal(...).quantize(..., ROUND_HALF_UP)`.
- La logique métier reste dans les services.
- Les identités viennent uniquement du jeton via `CurrentUser` ou `Token`.
- Les commentaires sont enregistrés mais ne sont pas affichés dans le MVP.

## 3. Étapes

Une étape = un commit (ou une PR) cohérent. L’ordre suit la pile applicative : base, métier, API, puis frontend.

### Étape 1 — Implémenter la clôture d’une réservation

- **Objectif** : permettre au propriétaire de passer une réservation active à `terminee`.

- **Fichiers touchés** :
  - `backend/app/repositories/reservation.py`
  - `backend/app/services/reservation.py`
  - `backend/app/routers/reservations.py`
  - `backend/app/schemas/reservation.py`
  - `backend/tests/test_reservations.py`
  - `backend/tests/test_openapi.py`

- **Changements** :
  - ajouter `ReservationService.complete(reservation_id, current_user)` ;
  - vérifier l’existence de la réservation ;
  - vérifier que l’utilisateur courant est propriétaire du matériel ;
  - accepter uniquement une réservation de statut `active` ;
  - affecter `statut = "terminee"` ;
  - ajouter `POST /reservations/{reservation_id}/cloturer` ;
  - répondre `200`, `401`, `403`, `404` ou `409` selon les cas ;
  - documenter les réponses d’erreur dans OpenAPI.

- **Tests à écrire** :
  - `test_ac_01_1_cloture_reservation_active_terminee`
  - `test_ac_01_2_cloture_sans_authentification_renvoie_401`
  - `test_ac_01_3_cloture_par_un_non_proprietaire_renvoie_403`
  - `test_ac_01_4_cloture_reservation_inexistante_renvoie_404`
  - `test_ac_01_5_cloture_reservation_terminee_ou_annulee_renvoie_409`

- **Critères d’acceptation couverts** : AC-01.1 à AC-01.5.

- **À savoir expliquer** :
  - la clôture vérifie les relations serveur côté service ;
  - seul le propriétaire du matériel peut clôturer ;
  - une réservation annulée ou déjà terminée ne peut pas être clôturée ;
  - l’identité provient du jeton ;
  - aucune logique d’autorisation n’est placée dans le router.

- **Vérification** :

  ```bash
  docker compose run --rm backend pytest \
    tests/test_reservations.py -k "ac_01"
  ```

### Étape 2 — Ajouter le modèle Avis et sa migration

- **Objectif** : créer durablement les données nécessaires aux avis avec les contraintes d’intégrité.

- **Fichiers touchés** :
  - `backend/app/models/avis.py`
  - `backend/app/models/reservation.py`
  - `backend/app/models/__init__.py`
  - `backend/alembic/versions/<revision>_avis.py`
  - `backend/tests/conftest.py`

- **Changements** :
  - ajouter le modèle SQLAlchemy `Avis` ;
  - créer `reservation_id` avec une clé étrangère vers `reservations.id` ;
  - configurer `ON DELETE CASCADE` sur `reservation_id` ;
  - rendre `reservation_id` unique avec la contrainte nommée `avis_reservation_uq` ;
  - ajouter les contraintes :
    - `avis_note_ck` : `note >= 1 AND note <= 5` ;
    - `avis_commentaire_ck` : `commentaire IS NULL OR char_length(commentaire) <= 500` ;
  - ajouter les relations nécessaires avec `Reservation` ;
  - exporter `Avis` depuis `app.models` ;
  - ajouter `avis` à la commande de nettoyage des fixtures ;
  - générer la migration avec Alembic, puis relire son `upgrade` et son `downgrade` ;
  - ne pas créer d’avis pour les réservations existantes.

- **Tests à écrire** :
  - `test_ac_02_9_base_refuse_une_note_hors_limites`
  - `test_ac_02_10_base_refuse_un_commentaire_trop_long`
  - `test_ac_02_8_base_refuse_un_second_avis_par_reservation`

- **Critères d’acceptation couverts** : AC-02.8, AC-02.9, AC-02.10.

- **À savoir expliquer** :
  - la contrainte unique protège aussi contre les requêtes concurrentes ;
  - les contraintes SQL complètent la validation Pydantic ;
  - `avis.reservation_id` utilise `ON DELETE CASCADE` ;
  - supprimer un objet supprime ses réservations en cascade, puis leurs avis ;
  - les contraintes sont nommées `avis_reservation_uq`, `avis_note_ck` et `avis_commentaire_ck` ;
  - les données existantes ne reçoivent aucun avis rétroactif ;
  - la migration doit avoir un `downgrade` propre.

- **Vérification** :

  ```bash
  docker compose run --rm backend pytest \
    tests/test_avis.py -k "base"
  ```

### Étape 3 — Implémenter la publication d’un avis

- **Objectif** : permettre à l’emprunteur d’ajouter un avis valide sur une réservation terminée.

- **Fichiers touchés** :
  - `backend/app/models/reservation.py`
  - `backend/app/repositories/avis.py`
  - `backend/app/services/avis.py`
  - `backend/app/routers/avis.py`
  - `backend/app/schemas/avis.py`
  - `backend/tests/test_avis.py`
  - `backend/tests/test_openapi.py`
  - `backend/app/main.py`

- **Changements** :
  - définir `AvisCreate` avec :
    - note entière stricte comprise entre 1 et 5 ;
    - commentaire optionnel limité à 500 caractères ;
  - ajouter `AvisRead` sans exposer les informations inutiles au MVP ;
  - ajouter `AvisRepository` ;
  - vérifier en concurrence la contrainte unique via une gestion ciblée de `IntegrityError` ;
  - ajouter `AvisService.create(reservation_id, payload, current_user)` ;
  - vérifier l’existence de la réservation ;
  - vérifier que l’utilisateur est l’emprunteur ;
  - vérifier que le statut est `terminee` ;
  - vérifier qu’aucun avis n’existe déjà ;
  - ajouter `POST /reservations/{reservation_id}/avis`, statut `201` ;
  - conserver les réponses `401`, `404`, `403`, `409` et `422`.
  - inclure `avis.router` dans `backend/app/main.py`.

- **Tests à écrire** :
  - `test_ac_02_1_publie_un_avis_entier_sur_reservation_terminee`
  - `test_ac_02_2_publie_un_avis_sans_commentaire`
  - `test_ac_02_3_publie_un_commentaire_de_500_caracteres`
  - `test_ac_02_4_publie_sans_authentification_renvoie_401`
  - `test_ac_02_5_publie_pour_reservation_inexistante_renvoie_404`
  - `test_ac_02_6_publie_sur_reservation_d_un_autre_emprunteur_renvoie_403`
  - `test_ac_02_7_publie_sur_reservation_active_ou_annulee_renvoie_409`
  - `test_ac_02_8_publie_un_second_avis_renvoie_409`
  - `test_ac_02_9_valide_une_note_obligatoire_entiere_et_entre_1_et_5`
  - `test_ac_02_10_refuse_un_commentaire_superieur_a_500_caracteres`

- **Critères d’acceptation couverts** : AC-02.1 à AC-02.10.

- **À savoir expliquer** :
  - Pydantic interdit les notes décimales, absentes et hors limites ;
  - le commentaire optionnel est limité à 500 caractères ;
  - l’identité ne peut pas être fournie dans le corps ;
  - la contrainte unique protège les publications concurrentes ;
  - les statuts actifs ou annulés sont refusés avec `409`.

- **Vérification** :

  ```bash
  docker compose run --rm backend pytest \
    tests/test_avis.py
  ```

### Étape 4 — Calculer la réputation du propriétaire

- **Objectif** : fournir la moyenne et le nombre d’avis reçus sur tous les matériels du propriétaire.

- **Fichiers touchés** :
  - `backend/app/repositories/avis.py`
  - `backend/app/repositories/item.py`
  - `backend/app/services/item.py`
  - `backend/app/schemas/item.py`
  - `backend/tests/test_items.py`

- **Changements** :
  - ajouter une agrégation reliant :
    - `Avis` ;
    - `Reservation` ;
    - `Item.owner_id` ;
  - compter tous les avis des matériels du même propriétaire ;
  - calculer la moyenne sur les réservations terminées ;
  - arrondir avec `ROUND_HALF_UP` à une décimale ;
  - ajouter `reputation_moyenne` et `reputation_nombre` à un schéma de détail ;
  - conserver `ItemRead` pour les listes sans calcul de réputation ;
  - renvoyer `None` et `0` lorsqu’il n’existe aucun avis ;
  - ne pas afficher les commentaires individuels.

- **Tests à écrire** :
  - `test_ac_03_1_detail_public_affiche_moyenne_et_nombre_d_avis`
  - `test_ac_03_2_detail_public_sans_avis_affiche_aucune_reputation`
  - `test_ac_03_3_moyenne_calculee_sur_tous_les_avis_du_preteur`

- **Critères d’acceptation couverts** : AC-03.1 à AC-03.3.

- **À savoir expliquer** :
  - l’agrégation porte sur le propriétaire, pas uniquement sur l’objet consulté ;
  - une seule lecture agrégée suffit pour le volume actuel ;
  - l’arrondi backend évite les divergences d’affichage ;
  - la moyenne reste dynamique ;
  - la liste des annonces ne calcule pas la réputation dans le MVP.

- **Vérification** :

  ```bash
  docker compose run --rm backend pytest \
    tests/test_items.py -k "ac_03"
  ```

### Étape 5 — Afficher les actions métier et la réputation dans le frontend

- **Objectif** : rendre les fonctions utilisables depuis les pages existantes.

- **Fichiers touchés** :
  - `frontend/app/api_client.py`
  - `frontend/app/routers/items.py`
  - `frontend/app/routers/reservations.py`
  - `frontend/app/templates/items/detail.html`

- **Changements** :
  - ajouter dans `ApiClient` :
    - `complete_reservation` ;
    - `create_review` ;
  - ajouter dans le router frontend :
    - `POST /reservations/{reservation_id}/cloturer` ;
    - `POST /reservations/{reservation_id}/avis` ;
  - ajouter un appel à l’API pour connaître l’utilisateur courant si nécessaire ;
  - afficher sur le détail :
    - `4.3/5 (12 avis)` ;
    - `Aucun avis` ;
  - afficher le bouton de clôture uniquement pour le propriétaire et une réservation active ;
  - afficher le formulaire d’avis uniquement pour l’emprunteur d’une réservation terminée ;
  - rendre le commentaire optionnel ;
  - gérer les erreurs `401`, `403`, `404`, `409` et `422` avec des messages visibles ;
  - laisser le formulaire visible après un avis existant : l’API refuse le doublon et le frontend affiche son message d’erreur ;
  - conserver la réservation comme flux principal dans le détail.

- **Critères d’acceptation couverts** : interface de AC-01.1 à AC-03.3.

- **À savoir expliquer** :
  - l’identité affichée est dérivée de `/auth/me`, pas du formulaire ;
  - le frontend adapte les actions visibles mais ne remplace jamais les contrôles backend ;
  - les doubles publications restent refusées par l’API ;
  - les commentaires ne sont pas affichés ;
  - les visiteurs voient uniquement la réputation publique.

- **Vérification** :
  - démarrer avec `docker compose up` ;
  - effectuer les parcours décrits dans la recette manuelle ;
  - aucune validation d’interface automatisée n’est disponible tant qu’une telle suite n’est pas ajoutée.

### Étape 6 — Recette finale

- **Objectif** : vérifier la couverture, la qualité et les parcours manuels de la feature.

- **Fichiers touchés** : aucun.

- **Changements** :
  - les tests restent écrits dans les étapes 1 à 4 ;
  - recenser les noms `test_ac_<story>_<critère>_...` ;
  - exécuter la suite complète ;
  - exécuter le lint ;
  - effectuer la recette manuelle décrite ci-dessous.

- **À savoir expliquer** :
  - `grep -rn "test_ac_" tests` vérifie que les tests sont nommés selon la convention ;
  - la suite pytest couvre les contraintes, les routes et les règles métier ;
  - le lint vérifie le backend et le frontend ;
  - la recette manuelle valide les parcours visibles et les erreurs UX ;
  - cette étape ne doit pas nécessiter l’ajout d’un nouveau test.

- **Vérification** :

  ```bash
  grep -rn "test_ac_" tests
  docker compose run --rm backend pytest
  docker run --rm -v "$PWD":/src -w /src python:3.12-slim sh -c "pip install -q ruff==0.17.3 && ruff check backend frontend"
  ```

  Puis jouer la recette manuelle de la section 6.

## 4. Traçabilité critères → tests

Chaque critère de la fiche apparaît ici.

| Critère | Test | Étape |
|---|---|---|
| AC-01.1 | `test_ac_01_1_cloture_reservation_active_terminee` | 1 |
| AC-01.2 | `test_ac_01_2_cloture_sans_authentification_renvoie_401` | 1 |
| AC-01.3 | `test_ac_01_3_cloture_par_un_non_proprietaire_renvoie_403` | 1 |
| AC-01.4 | `test_ac_01_4_cloture_reservation_inexistante_renvoie_404` | 1 |
| AC-01.5 | `test_ac_01_5_cloture_reservation_terminee_ou_annulee_renvoie_409` | 1 |
| AC-02.1 | `test_ac_02_1_publie_un_avis_entier_sur_reservation_terminee` | 3 |
| AC-02.2 | `test_ac_02_2_publie_un_avis_sans_commentaire` | 3 |
| AC-02.3 | `test_ac_02_3_publie_un_commentaire_de_500_caracteres` | 3 |
| AC-02.4 | `test_ac_02_4_publie_sans_authentification_renvoie_401` | 3 |
| AC-02.5 | `test_ac_02_5_publie_pour_reservation_inexistante_renvoie_404` | 3 |
| AC-02.6 | `test_ac_02_6_publie_sur_reservation_d_un_autre_emprunteur_renvoie_403` | 3 |
| AC-02.7 | `test_ac_02_7_publie_sur_reservation_active_ou_annulee_renvoie_409` | 3 |
| AC-02.8 | `test_ac_02_8_publie_un_second_avis_renvoie_409` | 2, 3 |
| AC-02.9 | `test_ac_02_9_valide_une_note_obligatoire_entiere_et_entre_1_et_5` | 2, 3 |
| AC-02.10 | `test_ac_02_10_refuse_un_commentaire_superieur_a_500_caracteres` | 2, 3 |
| AC-03.1 | `test_ac_03_1_detail_public_affiche_moyenne_et_nombre_d_avis` | 4 |
| AC-03.2 | `test_ac_03_2_detail_public_sans_avis_affiche_aucune_reputation` | 4 |
| AC-03.3 | `test_ac_03_3_moyenne_calculee_sur_tous_les_avis_du_preteur` | 4 |

## 5. Migration et retour arrière

- La migration crée uniquement la table `avis` et ses contraintes.
- Elle est réversible via `downgrade`.
- Les données existantes restent inchangées : aucune réservation existante ne reçoit d’avis.
- Pour annuler la feature après livraison :
  - appliquer le `downgrade` de la migration ;
  - supprimer les routes et éléments frontend associés ;
  - supprimer les schémas, services, repositories et modèles devenus inutilisés.
- Aucun secret ni donnée sensible n’est introduit.

## 6. Recette manuelle

Le parcours à jouer dans le navigateur avant de déclarer la feature terminée.

1. Se connecter comme propriétaire.
2. Ouvrir une réservation active de son matériel.
3. Cliquer sur « Clôturer ».
4. Vérifier que la réservation passe à `terminee`.
5. Recharger la page et vérifier que la clôture ne peut pas être faite une seconde fois.
6. Se connecter avec l’emprunteur de cette réservation.
7. Publier une note de 1 à 5 avec un commentaire court.
8. Vérifier que le second envoi est refusé.
9. Se déconnecter.
10. Ouvrir l’annonce du prêteur.
11. Vérifier l’affichage `4.3/5 (12 avis)` ou l’arrondi correspondant.
12. Ouvrir une annonce d’un prêteur sans avis.
13. Vérifier l’affichage exact `Aucun avis`.
14. Vérifier qu’un visiteur peut consulter la réputation sans être connecté.
15. Vérifier qu’un utilisateur non emprunteur ne peut pas publier d’avis.
