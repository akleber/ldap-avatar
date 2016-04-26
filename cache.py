#!/usr/local/bin/python
# coding: ascii

import sqlite3
import argparse
import os.path

CACHE_SCHEMA = os.path.join(os.path.dirname(__file__),'cache-schema.sql')
CACHE_DUMP = os.path.join(os.path.dirname(__file__),'cache-dump.sql')
CACHE_FILE = os.path.join(os.path.dirname(__file__),'cache.db')

def init_cache(cache):
	f = open(CACHE_SCHEMA,'r')
	sql = f.read()
	cache.executescript(sql)

def dump_cache(cache):
	with open(CACHE_DUMP, 'w') as f:
		for line in cache.iterdump():
			f.write('%s\n' % line)

def connect_cache():
	cache = None

	# check if file exists
	if (not os.path.isfile(CACHE_FILE)):
		cache = sqlite3.connect(CACHE_FILE, detect_types=sqlite3.PARSE_DECLTYPES)
		init_cache(cache)
		poppulate_cache(cache)
	else:
		cache = sqlite3.connect(CACHE_FILE, detect_types=sqlite3.PARSE_DECLTYPES)

	return cache

def poppulate_cache(cache):
	#TODO load some static items from files
	pass

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Cache')
	parser.add_argument('--init', help='Init the Cache', action="store_true")
	parser.add_argument('--dump', help='Dump the Cache', action="store_true")
	args = parser.parse_args()

	cache = None

	try:
		cache = connect_db()

		if (args.init):
			init_db(cache)
		elif(args.dump):
			dump_db(cache)

	finally:
		if cache:
			cache.close()

