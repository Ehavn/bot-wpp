from bson import ObjectId

class MessageDAO:
    def __init__(self, db_client, config: dict):
        self.db = db_client[config["db_name"]]
        self.collection_raw = self.db[config["collection_raw"]]
        self.collection_sanitize = self.db[config["collection_sanitize"]]

    def get_pending_messages(self):
        return list(self.collection_raw.find({"status": "pending"}))

    def get_sanitized_messages(self):
        return list(self.collection_raw.find({"status": "sanitized"}))

    def update_message_status(self, message_id, status, new_content=None):
        update_fields = {"status": status}
        if new_content is not None:
            update_fields["content"] = new_content
        self.collection_raw.update_one(
            {"_id": ObjectId(message_id)},
            {"$set": update_fields}
        )

    def insert_sanitized_message(self, data):
        self.collection_sanitize.insert_one(data)
