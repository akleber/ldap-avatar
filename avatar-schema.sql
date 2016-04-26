BEGIN TRANSACTION;

DROP TABLE IF EXISTS 'photos';
CREATE TABLE 'photos' (
  'photo_hash' TEXT NOT NULL PRIMARY KEY,
  'photo'   BLOB NOT NULL
);

DROP TABLE IF EXISTS 'emails';
CREATE TABLE 'emails' (
  'photo_hash'    TEXT NOT NULL,
  'email_address' TEXT NOT NULL,
  'email_hash'    TEXT NOT NULL,
  FOREIGN KEY('photo_hash') REFERENCES 'photos'('photo_hash')
);

CREATE INDEX 'email_hash_index' ON 'emails' ('email_hash');

COMMIT;
