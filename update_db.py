#!/usr/local/bin/python
# coding: utf-8

import sqlite3
import database
import ldap_access
import hashlib
import ConfigParser
import os

def add_users_from_ldap(db):
        added_users = 0

        user_infos = ldap_access.get_user_infos()

        with db:
            c = db.cursor()

            c.execute("SELECT photo_hash FROM photos")
            rows = c.fetchall()
            all_photo_hashes = [r[0] for r in rows]

            for smtp_addresses, photo in user_infos:
                photo_hash = hashlib.md5(photo).hexdigest()

                if not photo_hash in all_photo_hashes:
                    added_users += 1
                    c.execute("INSERT INTO photos (photo_hash, photo) VALUES (?, ?)", [photo_hash, sqlite3.Binary(photo)])

                    for email_address in smtp_addresses:
                        email_hash = hashlib.md5(email_address.lower()).hexdigest()
                        c.execute("INSERT INTO emails (photo_hash, email_address, email_hash) VALUES (?, ?, ?)",
                            [photo_hash, email_address, email_hash])

            db.commit()

        print("Added {} users".format(added_users))


def add_users_from_static(db):
    added_users = 0

    static_dir_name = os.path.join(os.path.dirname(__file__),'static')
    files = [os.path.join(static_dir_name, f) for f in os.listdir(static_dir_name) if os.path.isfile(os.path.join(static_dir_name, f))]

    with db:
        c = db.cursor()

        c.execute("SELECT photo_hash FROM photos")
        rows = c.fetchall()
        all_photo_hashes = [r[0] for r in rows]

        for file in files:
            with open(file, "rb") as f:
                photo = f.read()

            photo_hash = hashlib.md5(photo).hexdigest()

            if not photo_hash in all_photo_hashes:
                added_users += 1
                c.execute("INSERT INTO photos (photo_hash, photo) VALUES (?, ?)", [photo_hash, sqlite3.Binary(photo)])

                email_address = os.path.splitext(os.path.basename(file))[0]

                email_hash = hashlib.md5(email_address.lower()).hexdigest()
                c.execute("INSERT INTO emails (photo_hash, email_address, email_hash) VALUES (?, ?, ?)",
                    [photo_hash, email_address, email_hash])

        db.commit()

    print("Added {} users from static files".format(added_users))


def remove_email_hashes(db):
    config = ConfigParser.RawConfigParser()
    config.read('avatar.cfg')
    EMAIL_HASHES_TO_REMOVE = config.get('DB', 'EMAIL_HASHES_TO_REMOVE')

    email_hashes = EMAIL_HASHES_TO_REMOVE.split()
    removes_email_hashes = 0

    with db:
        c = db.cursor()

        for email_hash in email_hashes:
            removes_email_hashes += 1
            c.execute("DELETE FROM emails WHERE email_hash=?", [email_hash])

        db.commit()

    print("Removed {} email hashes".format(removes_email_hashes))


def main():
    db = None

    try:
        db = database.connect_db()

        add_users_from_ldap(db)
        add_users_from_static(db)
        remove_email_hashes(db)

    finally:
        if db:
            db.close()

if __name__ == '__main__':
    main()
