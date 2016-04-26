BEGIN TRANSACTION;

DROP TABLE IF EXISTS cache;
CREATE TABLE cache (
    email_hash TEXT NOT NULL,
    size INTEGER,
    photo BLOB NOT NULL
);

CREATE INDEX email_hash_index ON cache (email_hash, size);

COMMIT;
