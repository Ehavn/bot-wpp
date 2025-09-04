# Arquivo: src/dao/message_dao.py
# VERSÃO FINAL COM CONVERSÃO DE DATETIME

from bson import ObjectId
from datetime import datetime

class MessageDAO:
    def __init__(self, db_client, config: dict):
        self.db = db_client[config["db_name"]]
        self.collection_messages = self.db[config["collection_raw"]]

    def save_raw_message(self, message_data: dict) -> ObjectId:
        message_data['status'] = 'pending'
        result = self.collection_messages.insert_one(message_data)
        return result.inserted_id

    def find_and_update_one_pending_message(self):
        return self.collection_messages.find_one_and_update(
            {'status': 'pending'},
            {'$set': {'status': 'processing'}}
        )

    def mark_message_as_processed(self, message_id: ObjectId):
        self.collection_messages.update_one(
            {'_id': message_id},
            {'$set': {'status': 'processed'}}
        )
    
    def mark_message_as_failed(self, message_id: ObjectId):
        self.collection_messages.update_one(
            {'_id': message_id},
            {'$set': {'status': 'failed'}}
        )

    def get_history(self, conversation_id: str, current_message_id: ObjectId, limit: int = 20) -> list:
        """
        Busca o histórico de uma conversa e retorna em um formato 100% JSON serializável.
        """
        query = {
            "$or": [
                {"conversationId": conversation_id},
                {"from": conversation_id}
            ],
            "_id": {"$ne": current_message_id}
        }
        
        cursor = self.collection_messages.find(query).sort("created_at", -1).limit(limit)
        
        history = []
        for doc in cursor:
            # --- PONTO DA CORREÇÃO ---
            # Converte ObjectId e datetime para strings aqui, garantindo a serialização.
            doc["_id"] = str(doc["_id"])
            if 'created_at' in doc and isinstance(doc['created_at'], datetime):
                doc['created_at'] = doc['created_at'].isoformat()
            
            history.append(doc)
            
        history.reverse()
        return history