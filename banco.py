from pymongo import MongoClient
from flask import current_app, g

def get_db():
    if 'mongo' not in g:
        uri = current_app.config.get("MONGO_URI", "mongodb://localhost:27017/")
        client = MongoClient(uri)

        g.mongo = client
        g.db = client[current_app.config.get("MONGO_DBNAME", "meu_banco")]

    return g.db