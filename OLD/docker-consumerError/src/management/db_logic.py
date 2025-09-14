from bson import ObjectId
from src.utils.mongo_client import get_mongo_client

def get_collection():
    client, config = get_mongo_client()
    db = client[config["db_name"]]
    return db[config["collection_dead_letter"]]

def list_failed_messages():
    collection = get_collection()
    return list(collection.find({"status": "unresolved"}, {"original_message.content": 1, "failed_at": 1}))

def get_failed_message(message_id):
    collection = get_collection()
    return collection.find_one({"_id": ObjectId(message_id)})

def update_status(message_id, status):
    collection = get_collection()
    result = collection.update_one({"_id": ObjectId(message_id)}, {"$set": {"status": status}})
    return result.modified_count > 0