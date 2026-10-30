# Prompts, contrainte EXCLUDE

Contexte : j'ai ajouté moi-même la contrainte EXCLUDE reservations_active_no_overlap dans backend/app/models/reservation.py et la migration Alembic 282ac4d65b77 (écrite à la main car autogenerate ne la détecte pas). Ne modifie pas ces deux fichiers.

Objectif : la base refuse deux réservations actives qui se chevauchent sur le même item, même si deux requêtes passent la vérification has_active_overlap en même temps. L'API doit alors renvoyer 409 et pas 500.

1. backend/tests/conftest.py : dans la fixture engine, avant drop_all, exécuter CREATE EXTENSION IF NOT EXISTS btree_gist (sinon create_all échoue sur gearshare_test).

2. backend/app/repositories/reservation.py, méthode add :
   - faire add + flush dans un savepoint (self.db.begin_nested()) pour que la session reste utilisable après une erreur ;
   - attraper IntegrityError ; si exc.orig.diag.constraint_name vaut "reservations_active_no_overlap", lever ConflitMetier("Le créneau demandé est déjà réservé") avec from exc, sinon relancer l'erreur ;
   - garder le nom de la contrainte dans une constante du module.
   La vérification has_active_overlap du service reste en place.

3. backend/tests/test_reservations.py, ajouter à la fin une section « Contrainte EXCLUDE en base » sans modifier les tests existants :
   - insertion directe en session (sans le service) d'une réservation active qui chevauche reservation_active : IntegrityError qui mentionne reservations_active_no_overlap (utiliser db.begin_nested()) ;
   - même insertion après avoir passé reservation_active en "annulee" : acceptée ;
   - réservation jointive (date_debut = date_fin de reservation_active) : acceptée ;
   - course simulée : monkeypatch de ReservationRepository.has_active_overlap pour renvoyer False, POST /reservations qui chevauche avec client_bob : 409 avec {"detail": "Le créneau demandé est déjà réservé"}, et la liste des réservations de l'item n'en contient toujours qu'une.

4. Lance les tests avec docker compose exec backend pytest -q et donne-moi le résultat.

5. Ajoute ce prompt tel quel dans docs/features/01-pas-de-double-reservation/prompts.md (crée le fichier, titre « Prompts, contrainte EXCLUDE »).

Pas de commentaire inutile dans le code. Pas de commit.
