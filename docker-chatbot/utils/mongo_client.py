import json
from pymongo import MongoClient

def load_mongo_config(config_file="config/config.json"):
    """Carrega configurações do MongoDB do config unificado."""
    with open(config_file, "r") as f:
        config = json.load(f)
    mongo_config = config.get("mongo", {})
    if not mongo_config.get("connectionUri"):
        raise ValueError("connectionUri não encontrado na seção mongo do config.json")
    return mongo_config

def get_mongo_client(config_file="config/config.json"):
    """Cria e retorna cliente Mongo e config."""
    mongo_config = load_mongo_config(config_file)
    client = MongoClient(
        mongo_config["connectionUri"],
        tls=True,
        tlsAllowInvalidCertificates=True  # se necessário para testes
    )
    return client, mongo_config
