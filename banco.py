import os
from pymongo import MongoClient
from flask import current_app, g

def get_db():
    if 'mongo' not in g:
        uri = os.environ.get("MONGO_URI")
        dbname = os.environ.get("MONGO_DBNAME", "banco_lojinha")

        client = MongoClient(uri)

        g.mongo = client
        g.db = client[dbname]

    return g.db