CREATE EXTENSION IF NOT EXISTS btree_gist;

ALTER TABLE reservations
    DROP CONSTRAINT reservations_borrower_id_fkey,
    ADD CONSTRAINT reservations_borrower_fk
        FOREIGN KEY (borrower_id) REFERENCES users(id) ON DELETE RESTRICT;

CREATE INDEX items_owner_id_idx ON items (owner_id);
CREATE INDEX reservations_item_id_idx ON reservations (item_id);
CREATE INDEX reservations_borrower_id_idx ON reservations (borrower_id);

CREATE TABLE avis (
    id             BIGSERIAL,
    reservation_id BIGINT      NOT NULL,
    note           INTEGER     NOT NULL,
    commentaire    TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT avis_pk PRIMARY KEY (id),
    CONSTRAINT avis_reservation_uq UNIQUE (reservation_id),
    CONSTRAINT avis_reservation_fk
        FOREIGN KEY (reservation_id) REFERENCES reservations(id) ON DELETE CASCADE,
    CONSTRAINT avis_note_ck CHECK (note BETWEEN 1 AND 5)
);

CREATE TABLE tags (
    id        BIGSERIAL,
    libelle   VARCHAR(50) NOT NULL,
    CONSTRAINT tags_pk PRIMARY KEY (id),
    CONSTRAINT tags_libelle_uq UNIQUE (libelle),
    CONSTRAINT tags_libelle_minuscule_ck CHECK (libelle = lower(libelle))
);

CREATE TABLE item_tags (
    item_id BIGINT NOT NULL,
    tag_id  BIGINT NOT NULL,
    CONSTRAINT item_tags_pk PRIMARY KEY (item_id, tag_id),
    CONSTRAINT item_tags_item_fk
        FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    CONSTRAINT item_tags_tag_fk
        FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE INDEX item_tags_tag_id_idx ON item_tags (tag_id);

ALTER TABLE reservations
    ADD CONSTRAINT reservations_active_no_overlap
    EXCLUDE USING gist (
        item_id WITH =,
        daterange(date_debut, date_fin, '[)') WITH &&
    ) WHERE (statut = 'active');

CREATE FUNCTION verifier_avis_reservation_terminee()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM reservations
        WHERE id = NEW.reservation_id
          AND statut <> 'terminee'
    ) THEN
        RAISE EXCEPTION 'Un avis doit concerner une réservation terminée';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER avis_reservation_terminee_trg
BEFORE INSERT OR UPDATE OF reservation_id ON avis
FOR EACH ROW
EXECUTE FUNCTION verifier_avis_reservation_terminee();