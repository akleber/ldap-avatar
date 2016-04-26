#!/usr/bin/python

import falcon
import database
import cache
import logging
import identicon.identicon as identicon
import io
import os
import sqlite3
from PIL import Image

#logging.basicConfig(filename=os.path.join(os.path.dirname(__file__),'avatar.log'),level=logging.DEBUG)
#logging.basicConfig(level=logging.DEBUG)

class Avatar(object):

    def put_photo_in_cache(self, email_hash, size, photo):
        logging.debug("put photo for hash %s with size %d into cache", email_hash, size)
        cache_con = cache.connect_cache()
        c = cache_con.cursor()
        c.execute("INSERT INTO cache (email_hash, size, photo) VALUES (?, ?, ?)", [email_hash, size, sqlite3.Binary(photo)])
        cache_con.commit()
        cache_con.close()


    def get_photo_from_cache(self, email_hash, size):
        found = False
        photo = None

        cache_con = cache.connect_cache()
        c = cache_con.cursor()
        c.execute("SELECT photo FROM cache WHERE email_hash = ? AND size = ?", [email_hash,size])
        photodata = c.fetchone()
        if photodata:
            found = True
            photo = bytes(photodata[0])

        cache_con.close()

        return (found, photo)


    def get_photo_from_db(self, email_hash):
        found = False
        photo = None

        db = database.connect_db()
        c = db.cursor()
        c.execute("SELECT photo_hash FROM emails WHERE email_hash = ?", [email_hash])
        photo_hash = c.fetchone()
        if photo_hash:
            c.execute("SELECT photo FROM photos WHERE photo_hash = ?", [photo_hash[0]])
            photodata = c.fetchone()

            if photodata:
                found = True
                photo = bytes(photodata[0])

        db.close()

        return (found, photo)

    def resize_and_square(self, photo, size):
        file_in = io.BytesIO(photo)
        file_in.seek(0)
        img = Image.open(file_in)

        #from: http://javiergodinez.blogspot.de/2008/03/square-thumbnail-with-python-image.html
        width, height = img.size

        if width > height:
            delta = width - height
            left = int(delta/2)
            upper = 0
            right = height + left
            lower = height
        else:
            delta = height - width
            left = 0
            upper = int(delta/2)
            right = width
            lower = width + upper

        img = img.crop((left, upper, right, lower))
        img.thumbnail((size,size))

        file_out = io.BytesIO()
        img.save(file_out, 'PNG')

        return file_out.getvalue()


    def on_get(self, req, resp, email_hash):
        resp.content_type = "image/png"

        #cut possible extensions, we do not support them
        email_hash = email_hash[:32]

        size = 80
        if req.get_param("s"):
            size = int(req.get_param("s"))
        if req.get_param("size"):
            size = int(req.get_param("size"))

        # look for photo in cache
        found, photo = self.get_photo_from_cache(email_hash, size)
        if found:
            #logging.debug("hash %s with size %d found in cache", email_hash, size)
            pass

        else:
            # photo not found in cache, look in db
            found, photo = self.get_photo_from_db(email_hash)
            if found:
                logging.debug("hash %s found in db", email_hash)

                photo = self.resize_and_square(photo, size)

                self.put_photo_in_cache(email_hash, size, photo)

            else:
                # photo not found in db, render identicon
                logging.debug("hash %s NOT found, rendering identicon", email_hash)

                code = abs(hash(email_hash)) % (10 ** 8)
                icon = identicon.render_identicon(code, size)
                icon.thumbnail((size,size))

                b = io.BytesIO()
                icon.save(b, 'PNG')
                photo = b.getvalue()

                self.put_photo_in_cache(email_hash, size, photo)

        resp.status = falcon.HTTP_200
        resp.body = photo


# entry
api = application = falcon.API()
api.add_route('/{email_hash}', Avatar())



