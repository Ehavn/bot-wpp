<<<<<<< HEAD
import json
from pymongo import MongoClient

def load_config():
    with open("config/config.json", "r") as f:
        return json.load(f)

def get_mongo_client():
    config = load_config()
    mongo_config = config.get("mongodb")
    if not mongo_config:
        raise ValueError("Chave 'mongodb' não encontrada no config")
    
    connection_uri = mongo_config.get("connectionUri")
    if not connection_uri:
        raise ValueError("connectionUri não encontrado no config['mongodb']")
    
    client = MongoClient(connection_uri)
    return client, mongo_config
=======
import json
from pymongo import MongoClient

def load_config():
    with open("config/config.json", "r") as f:
        return json.load(f)

def get_mongo_client():
    config = load_config()
    mongo_config = config.get("mongodb")
    if not mongo_config:
        raise ValueError("Chave 'mongodb' não encontrada no config")
    
    connection_uri = mongo_config.get("connectionUri")
    if not connection_uri:
        raise ValueError("connectionUri não encontrado no config['mongodb']")
    
    client = MongoClient(connection_uri)
    return client, mongo_config
>>>>>>> cccf66339631c294e783b616174331c055f49216
