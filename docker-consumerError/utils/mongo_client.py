import json
from pymongo import MongoClient

def load_config():
    with open("config/config.json", "r") as f:
        return json.load(f)

def get_mongo_client():
    config = load_config()["mongo"]
    connection_uri = config.get("connectionUri")
    if not connection_uri:
        raise ValueError("connectionUri não encontrado no config.json")

    client = MongoClient(connection_uri)
    return client, config