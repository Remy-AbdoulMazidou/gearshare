-- Insertions qui doivent échouer après 03-schema-v2.sql.
-- Lancement : docker compose exec -T db psql -U gearshare -d gearshare < sql/tests-contraintes.sql
-- Résultats relevés le 22/10 sur une base reconstruite avec down -v puis up -d.

-- 1. Note à 6 (réservation 1, terminée)
INSERT INTO avis (reservation_id, note) VALUES (1, 6);
-- ERROR: new row for relation "avis" violates check constraint "avis_note_ck"

-- 2. Deux avis sur la même réservation
BEGIN;
INSERT INTO avis (reservation_id, note, commentaire) VALUES (1, 5, 'Vélo en bon état');
INSERT INTO avis (reservation_id, note) VALUES (1, 4);
ROLLBACK;
-- Le premier INSERT passe, le deuxième donne :
-- ERROR: duplicate key value violates unique constraint "avis_reservation_uq"
-- DETAIL: Key (reservation_id)=(1) already exists.

-- 3. Deux tags avec le même libellé
BEGIN;
INSERT INTO tags (libelle) VALUES ('velo');
INSERT INTO tags (libelle) VALUES ('velo');
ROLLBACK;
-- ERROR: duplicate key value violates unique constraint "tags_libelle_uq"
-- DETAIL: Key (libelle)=(velo) already exists.

-- 4. Avis sur une réservation qui n'existe pas
INSERT INTO avis (reservation_id, note) VALUES (999, 4);
-- ERROR: insert or update on table "avis" violates foreign key constraint "avis_reservation_fk"
-- DETAIL: Key (reservation_id)=(999) is not present in table "reservations".

-- 5. Tag avec une majuscule
INSERT INTO tags (libelle) VALUES ('Sport');
-- ERROR: new row for relation "tags" violates check constraint "tags_libelle_minuscule_ck"

-- 6. Avis sur une réservation encore active (réservation 2)
INSERT INTO avis (reservation_id, note) VALUES (2, 4);
-- ERROR: Un avis doit concerner une réservation terminée
-- CONTEXT: PL/pgSQL function verifier_avis_reservation_terminee() line 9 at RAISE

-- 7. Réservation active qui chevauche la réservation 2 sur la tente (item 3, du 10 au 12/09)
INSERT INTO reservations (item_id, borrower_id, date_debut, date_fin)
VALUES (3, 3, '2026-09-11', '2026-09-14');
-- ERROR: conflicting key value violates exclusion constraint "reservations_active_no_overlap"
-- DETAIL: (3, [2026-09-11,2026-09-14)) conflicts with existing key (3, [2026-09-10,2026-09-12)).
