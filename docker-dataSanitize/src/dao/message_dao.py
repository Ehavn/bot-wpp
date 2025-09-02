# Arquivo: src/dao/message_dao.py

from bson import ObjectId

class MessageDAO:
    def __init__(self, db_client, config: dict):
        self.db = db_client[config["db_name"]]
        self.collection_raw = self.db[config["collection_raw"]]

    def save_raw_message(self, message_data: dict) -> ObjectId:
        """Salva a mensagem original com status inicial 'pending'."""
        message_data['status'] = 'pending'
        result = self.collection_raw.insert_one(message_data)
        return result.inserted_id

    def find_and_update_one_pending_message(self):
        """Encontra uma mensagem com status 'pending' e a atualiza para 'processing'."""
        return self.collection_raw.find_one_and_update(
            {'status': 'pending'},
            {'$set': {'status': 'processing'}}
        )

    def mark_message_as_processed(self, message_id: ObjectId):
        """Atualiza o status de uma mensagem para 'processed'."""
        self.collection_raw.update_one(
            {'_id': message_id},
            {'$set': {'status': 'processed'}}
        )
    
    def mark_message_as_failed(self, message_id: ObjectId):
        """Atualiza o status de uma mensagem para 'failed'."""
        self.collection_raw.update_one(
            {'_id': message_id},
            {'$set': {'status': 'failed'}}
        )

    def get_message_history_by_phone(self, phone_number: str, limit: int = 10) -> list:
        """
        Busca as últimas 'limit' mensagens de um número de telefone.
        """
        cursor = self.collection_raw.find(
            {"from": phone_number, "status": "processed"} 
        ).sort("timestamp", -1).limit(limit)
        
        history = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            history.append(doc)
            
        return history