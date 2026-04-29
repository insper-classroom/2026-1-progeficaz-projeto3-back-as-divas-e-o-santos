from pymongo import MongoClient
from flask import current_app, g

def get_db(): 
    if 'mongo' not in g:
        uri = current_app.config.get("MONGO_URI", "mongodb+srv://admin:12345@cluster0.i9nj5jh.mongodb.net/")
        client = MongoClient(uri)

        g.mongo = client
        g.db = client[current_app.config.get("MONGO_DBNAME", "meu_banco")]

    return g.db