# Fiche feature — Avis

**Statut** : validée
**Auteurs** : Rémy. Rédigé avec GitHub Copilot (mode Agent) à partir de mes réponses, relu et
corrigé par moi. Décisions de la section 7 prises par moi avec l'aide de Claude.
**Date** : 2026-11-22

## 1. Le problème

Les emprunteurs ne disposent d'aucun indice fiable pour savoir si un prêteur est sérieux avant de réserver son matériel. Une enquête auprès des utilisateurs de GearShare indique que six utilisateurs sur dix hésitent à emprunter du matériel à quelqu'un qu'ils ne connaissent pas.

Les prêteurs sérieux ne peuvent pas rendre visible la qualité de leurs prêts. Ils n'ont aucun moyen de capitaliser sur leur expérience ni de se constituer une réputation.

## 2. L'hypothèse et la métrique

> Si les emprunteurs peuvent voir la réputation d'un prêteur sur une annonce, alors ils oseront davantage réserver auprès d'un prêteur qu'ils ne connaissent pas.

- **Métrique principale** : part des réservations effectuées auprès d'un prêteur avec lequel l'emprunteur n'a encore jamais emprunté, comparée avant et après la mise en place de la fonctionnalité.
- **Métrique de suivi** : taux d'avis laissés après la clôture d'une réservation. Cette métrique permet de vérifier que la réputation affichée repose sur suffisamment d'avis.
- **Affichage cible** : moyenne sur une décimale et nombre d'avis, par exemple `4.3/5 (12 avis)`. Un objet sans avis affiche simplement `Aucun avis`.

## 3. Les utilisateurs concernés

- **Emprunteur** : vérifier la réputation du prêteur avant une réservation, puis noter sa propre expérience après la clôture du prêt.
- **Prêteur** : clôturer un prêt rendu et obtenir une réputation visible à partir des avis des emprunteurs.
- **Visiteur** : consulter la réputation d'un prêteur sans être connecté afin de décider si une annonce est fiable.

## 4. User stories et critères d'acceptation

### US-01 — Clôturer un prêt

En tant que prêteur, je veux clôturer une réservation lorsque le matériel a été rendu afin de rendre possible l'avis de l'emprunteur.

```text
AC-01.1  Given je suis connecté et je suis le propriétaire du matériel
         When je clôture une réservation encore active
         Then la réservation devient terminée

AC-01.2  Given je ne suis pas connecté
         When je tente de clôturer une réservation
         Then la clôture est refusée

AC-01.3  Given je suis connecté mais je ne suis pas le propriétaire du matériel
         When je tente de clôturer une réservation
         Then la clôture est refusée

AC-01.4  Given je tente de clôturer une réservation
         When cette réservation n'existe pas
         Then la clôture est refusée

AC-01.5  Given je suis le propriétaire du matériel
         When je tente de clôturer une réservation déjà terminée ou annulée
         Then la clôture est refusée
```

### US-02 — Laisser un avis

En tant qu'emprunteur, je veux noter le prêteur après une réservation terminée afin de partager mon expérience.

```text
AC-02.1  Given je suis connecté et je suis l'emprunteur d'une réservation terminée
         When je publie un avis avec une note entière de 1 à 5
         Then mon avis est enregistré

AC-02.2  Given je suis l'emprunteur d'une réservation terminée
         When je publie une note sans commentaire
         Then mon avis est enregistré

AC-02.3  Given je suis l'emprunteur d'une réservation terminée
         When je publie un commentaire contenant au plus 500 caractères
         Then le commentaire est accepté

AC-02.4  Given je ne suis pas connecté
         When je tente de publier un avis
         Then l'avis est refusé

AC-02.5  Given je tente de publier un avis
         When la réservation n'existe pas
         Then l'avis est refusé

AC-02.6  Given je suis connecté
         When je tente de publier un avis sur une réservation dont je ne suis pas l'emprunteur
         Then l'avis est refusé

AC-02.7  Given je suis l'emprunteur d'une réservation active ou annulée
         When je tente de publier un avis
         Then l'avis est refusé

AC-02.8  Given une réservation terminée possède déjà un avis
         When l'emprunteur tente d'en publier un second
         Then le second avis est refusé

AC-02.9  Given je suis l'emprunteur d'une réservation terminée
         When je publie un avis sans note, avec une note décimale, ou avec une note hors de 1 à 5
         Then l'avis est refusé

AC-02.10 Given je suis l'emprunteur d'une réservation terminée
          When je publie un commentaire de plus de 500 caractères
          Then l'avis est refusé
```

### US-03 — Consulter la réputation d'un prêteur

En tant que visiteur ou utilisateur connecté, je veux voir la réputation d'un prêteur sur une annonce afin de décider avec davantage de confiance.

```text
AC-03.1  Given une annonce appartient à un prêteur ayant des avis
         When je consulte l'annonce sans être connecté
         Then je vois sa moyenne sur une décimale et le nombre d'avis

AC-03.2  Given une annonce appartient à un prêteur n'ayant aucun avis
         When je consulte l'annonce
         Then je vois « Aucun avis »

AC-03.3  Given plusieurs emprunteurs ont laissé des avis sur des réservations terminées du même prêteur
         When je consulte une de ses annonces
         Then la moyenne affichée correspond à la moyenne de tous les avis reçus par ce prêteur
```

## 5. Hors périmètre

- Modifier ou supprimer un avis déjà publié.
- Noter l'emprunteur : cette version permet uniquement à l'emprunteur de noter le prêteur.
- Modération, signalement, masquage d'un avis ou fonctionnalité administrateur.
- Réponse du prêteur à un avis.
- Avis anonymes : l'avis reste lié à la réservation et à son emprunteur.
- Page de profil complète du prêteur et historique détaillé de ses avis.
- Affichage des commentaires sur les avis : le MVP affiche uniquement la moyenne et le nombre d'avis.
- Clôture automatique d'une réservation à sa date de fin.
- Notifications et rappels pour demander un avis.
- Délai limite pour publier un avis.

## 6. Évaluation technique

### 6.1. Impacts par couche

| Couche | Impact |
|---|---|
| Base de données (tables, contraintes, migration) | Une nouvelle entité d'avis est nécessaire pour relier une réservation, son emprunteur et une note entière. Une contrainte d'unicité garantit qu'une seule note existe par réservation. Des contraintes garantissent une note comprise entre 1 et 5 et un commentaire limité à 500 caractères. Une migration autogénérée est nécessaire. |
| Modèle métier (règles, où elles sont vérifiées) | La logique appartient aux services : seul le propriétaire du matériel peut clôturer une réservation active ; seul l'emprunteur peut publier un avis sur sa réservation terminée ; un avis en double est interdit ; la moyenne est calculée sur les avis du propriétaire du matériel. |
| API (routes, codes de statut) | Les opérations de clôture et de publication d'avis sont absentes de l'API actuelle. La consultation de la réputation doit rester accessible sans authentification depuis les ressources d'annonce. |
| Autorisation (qui a le droit de quoi) | L'identité doit continuer à provenir du jeton. Le propriétaire du matériel et l'emprunteur sont identifiés à partir des relations existantes entre réservation, matériel et utilisateur. |
| Frontend (écrans, formulaires) | La page d'annonce doit afficher la moyenne et le nombre d'avis ou l'état sans avis. La page de réservation ou d'annonce doit permettre au propriétaire de clôturer et à l'emprunteur autorisé de publier une note avec un commentaire optionnel. |
| Prérequis absents de l'existant | Il faut ajouter l'entité d'avis, sa migration, ses contraintes, ses repositories, ses schémas Pydantic, ses services et ses routes. Il faut aussi ajouter une action métier de clôture : le statut `terminee` existe déjà dans le modèle de réservation, mais aucune méthode métier ni aucune interface ne permet actuellement de l'utiliser. |

### 6.2. Risques

- **Sécurité** : empêcher toute publication fondée sur une identité du corps de la requête ; vérifier en permanence le propriétaire du matériel, l'emprunteur et le statut de la réservation côté serveur.
- **Données existantes** : aucune donnée d'avis n'existe actuellement. Une migration doit être compatible avec les réservations déjà présentes sans créer d'avis rétroactifs.
- **Performance** : la moyenne est calculée à la lecture par une requête d'agrégation, ce qui suffit au volume du projet. Afficher la réputation sur la liste des annonces demanderait une agrégation par prêteur sur chaque page, à faire sans N+1 : renvoyé à une itération suivante.
- **Intégrité** : garantir l'unicité d'un avis par réservation même en cas de requêtes concurrentes.
- **UX** : distinguer clairement une réservation active, annulée et terminée, afin qu'un emprunteur ne confonde pas clôture et annulation.

### 6.3. Taille estimée

**L** — Cette feature traverse la base de données, les règles métier, l'API, les autorisations et le frontend. Elle introduit deux nouvelles actions métier, plusieurs cas de refus, des contraintes d'intégrité et une nouvelle donnée visible publiquement.

## 7. Options et compromis

| Question | Option A | Option B | Décision et raison |
|---|---|---|---|
| Localisation de la réputation | Moyenne par prêteur sur l'ensemble de ses matériels | Moyenne par annonce uniquement | A. Le problème est la confiance envers une personne, pas envers un objet. La moyenne du prêteur est affichée sur chacune de ses annonces. |
| Précision affichée | Une décimale | Arrondi à l'entier le plus proche | A. Un arrondi à l'entier confondrait 3,6 et 4,4. |
| Caractère du commentaire | Commentaire optionnel | Commentaire obligatoire | A. Un commentaire obligatoire découragerait de laisser un avis. Une note seule vaut mieux que rien. |
| Affichage des avis | Moyenne et nombre uniquement | Moyenne, nombre et commentaires individuels | A. Afficher les commentaires avec le nom de l'emprunteur révélerait qui a emprunté quoi. Commentaires sans nom en V2. |
| Mise à jour de la moyenne | Calcul dynamique à chaque consultation | Moyenne précalculée ou mise en cache | A. Une requête d'agrégation suffit au volume du projet, et une valeur précalculée pourrait se désynchroniser. |
| Action de clôture | La clôture est une nouvelle action explicite | Le passage à `terminee` reste une modification du statut | A. La clôture n'a pas les mêmes droits que l'annulation (propriétaire seul) et n'accepte qu'une réservation active. L'actuel PATCH ne gère que l'annulation. |
| Délai de publication | Aucun délai dans le MVP | Fenêtre limitée de 30 jours | A. Garde le MVP petit. Un délai pourra venir en V2. |

## 8. MVP et itérations suivantes

- **MVP** : clôturer une réservation active par le propriétaire ; laisser un avis avec note entière obligatoire et commentaire optionnel de 500 caractères maximum ; empêcher les doublons ; afficher la moyenne sur une décimale et le nombre d'avis sur les annonces, ou « Aucun avis ».
- **V2** : noter l'emprunteur ; page de profil du prêteur avec historique détaillé ; réponses aux avis ; modération et signalement ; notifications ou rappels ; délai limité pour publier.
- **Plus tard / backlog** : moyenne précalculée ou mise en cache à grande échelle ; filtres ou classement des annonces par réputation ; statistiques avancées pour les prêteurs.

## 9. Questions ouvertes

Réponses de Rémy :

- Arrondi de la moyenne : arrondi classique à une décimale, fait par le backend.
- Réputation sur la liste des annonces : pas dans le MVP, seulement sur la page de détail (voir
  le risque de performance en 6.2).
- Seuil d'avis pour une réputation « fiable » : hors périmètre. Le nombre d'avis affiché à côté
  de la moyenne suffit pour le MVP.
