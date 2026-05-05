import os
from pymongo import MongoClient
from flask import current_app, g

def get_db():
    if 'mongo' not in g:
        uri = os.environ.get("MONGO_URI")
        dbname = os.environ.get("MONGO_DBNAME", "loja")

        print(f"Tentando conectar ao MongoDB: URI={uri}, DB={dbname}")
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')  # Test connection
            print("Conexão MongoDB bem-sucedida!")
            g.mongo = client
            g.db = client[dbname]
        except Exception as e:
            print(f"Erro de conexão MongoDB: {e}")
            g.db = None
        # Remove the extra client creation
        # client = MongoClient(uri)

    return g.db