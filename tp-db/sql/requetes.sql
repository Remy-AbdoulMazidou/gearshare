-- TP séance 3, étape 3 : requêtes testées dans psql sur le jeu de données de 02-seed.sql.
-- Résultats obtenus en commentaire sous chaque requête.

-- 1. Items disponibles à moins de 10 €/jour, triés par tarif croissant
SELECT id, titre, tarif_jour
FROM items
WHERE disponible = TRUE AND tarif_jour < 10
ORDER BY tarif_jour ASC;
-- 2 | Perceuse      | 5.00
-- 1 | Vélo de ville | 8.50

-- 2. Items dont le titre contient « velo », insensible à la casse
SELECT id, titre FROM items WHERE titre ILIKE '%velo%';
-- (0 rows)
-- ILIKE ignore la casse mais pas les accents : « Vélo » contient un é, pas un e.
-- Une recherche tolérante demanderait l'extension unaccent.

-- 3. Chaque item avec le nom de son propriétaire
SELECT i.id, i.titre, u.display_name AS proprietaire
FROM items AS i
JOIN users AS u ON u.id = i.owner_id
ORDER BY i.id;
-- 1 | Vélo de ville  | Alice
-- 2 | Perceuse       | Alice
-- 3 | Tente 2 places | Bob
-- 4 | Appareil photo | Bob

-- 4. Nombre de réservations par item, y compris les items jamais réservés
SELECT i.titre, COUNT(r.id) AS nb_reservations
FROM items AS i
LEFT JOIN reservations AS r ON r.item_id = i.id
GROUP BY i.id, i.titre
ORDER BY nb_reservations DESC, i.titre;
-- Appareil photo | 1
-- Tente 2 places | 1
-- Vélo de ville  | 1
-- Perceuse       | 0
-- Avec JOIN au lieu de LEFT JOIN, la Perceuse disparaît (3 lignes).
-- COUNT(r.id) et non COUNT(*) : sinon la Perceuse compterait 1.

-- 5. Par utilisateur : nombre d'items et tarif moyen, seulement s'il a publié au moins un item
SELECT u.display_name,
       COUNT(i.id) AS nb_items,
       ROUND(AVG(i.tarif_jour), 2) AS tarif_moyen
FROM users AS u
LEFT JOIN items AS i ON i.owner_id = u.id
GROUP BY u.id, u.display_name
HAVING COUNT(i.id) > 0
ORDER BY nb_items DESC, u.display_name;
-- Alice | 2 | 6.75
-- Bob   | 2 | 16.00
-- Chloé est éliminée par le HAVING (0 item), après le regroupement.

-- 6. Réservations actives commençant après le 1er septembre 2026
SELECT r.id, i.titre, u.display_name AS emprunteur, r.date_debut, r.date_fin
FROM reservations AS r
JOIN items AS i ON i.id = r.item_id
JOIN users AS u ON u.id = r.borrower_id
WHERE r.statut = 'active' AND r.date_debut > '2026-09-01'
ORDER BY r.date_debut;
-- 2 | Tente 2 places | Alice | 2026-09-10 | 2026-09-12
-- 3 | Appareil photo | Chloé | 2026-09-15 | 2026-09-20

-- 7. Les 2 items les plus chers, en sautant le premier
SELECT id, titre, tarif_jour
FROM items
ORDER BY tarif_jour DESC
LIMIT 2 OFFSET 1;
-- 3 | Tente 2 places | 12.00
-- 1 | Vélo de ville  | 8.50

-- 8. Montant de chaque réservation active : tarif journalier multiplié par le nombre de jours
SELECT r.id, i.titre, i.tarif_jour,
       r.date_fin - r.date_debut AS nb_jours,
       i.tarif_jour * (r.date_fin - r.date_debut) AS montant
FROM reservations AS r
JOIN items AS i ON i.id = r.item_id
WHERE r.statut = 'active'
ORDER BY r.id;
-- 2 | Tente 2 places | 12.00 | 2 | 24.00
-- 3 | Appareil photo | 20.00 | 5 | 100.00
-- La différence de deux DATE donne un entier : du 10 au 12, 2 jours (on compte les nuits).
