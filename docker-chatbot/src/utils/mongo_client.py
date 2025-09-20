# src/utils/mongo_client.py
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def get_mongo_client():
    """
    Cria e retorna um cliente do MongoDB e a configuração,
    lendo as informações das variáveis de ambiente.
    """
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("A variável de ambiente MONGO_URI não foi definida.")

    try:
        client = MongoClient(mongo_uri)
        # O comando ismaster é uma forma leve de testar a conexão.
        client.admin.command('ismaster')
    except ConnectionFailure as e:
        raise ConnectionFailure(f"Não foi possível conectar ao MongoDB: {e}") from e

    mongo_config = {
        "db_name": os.getenv("MONGO_DB_NAME", "messages"),
        "collection_messages": os.getenv("MONGO_COLLECTION_MESSAGES", "raw")
    }
    
    return client, mongo_config