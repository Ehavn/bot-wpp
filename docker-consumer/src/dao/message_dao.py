# Arquivo: src/dao/message_dao.py (Otimizado)

from bson import ObjectId
from datetime import datetime

class MessageDAO:
    def __init__(self, mongo_client, mongo_config):
        self.db = mongo_client[mongo_config["db_name"]]
        self.collection = self.db[mongo_config["collection_raw"]]

    def save_raw_message(self, message_data: dict) -> dict:
        """Salva a mensagem bruta e retorna o dicionário com o _id inserido."""
        message_data['createdAt'] = datetime.utcnow()
        result = self.collection.insert_one(message_data)
        message_data['_id'] = result.inserted_id
        return message_data

    def get_message_by_id(self, message_id: ObjectId) -> dict:
        """Busca uma mensagem específica pelo seu ObjectId."""
        return self.collection.find_one({"_id": message_id})

    def get_history(self, conversation_id: str, current_id: ObjectId, limit: int = 20):
        """
        Busca o histórico de mensagens de uma conversa, excluindo a mensagem atual.
        Usa $or para buscar tanto no campo 'conversationId' quanto no 'from'.
        NOTA: Após uma migração de dados para padronizar o campo 'conversationId',
        o $or pode ser removido para simplificar e otimizar a consulta.
        """
        query = {
            "$or": [
                {"conversationId": conversation_id},
                {"from": conversation_id}
            ],
            "_id": {"$ne": current_id}
        }
        
        cursor = self.collection.find(query).sort("_id", -1).limit(limit)
        
        history = list(cursor)
        history.reverse()
        return history

    def _update_message_status(self, message_id: ObjectId, status: str, reason: str = None):
        """Função auxiliar para atualizar o status de uma mensagem."""
        update_fields = {
            "$set": {
                "status": status,
                "updatedAt": datetime.utcnow()
            }
        }
        if reason:
            update_fields["$set"]["failureReason"] = reason
        
        self.collection.update_one(
            {"_id": message_id},
            update_fields
        )

    def mark_message_as_processed(self, message_id: ObjectId):
        """Marca uma mensagem como 'processed'."""
        self._update_message_status(message_id, "processed")

    def mark_message_as_failed(self, message_id: ObjectId, reason: str):
        """Marca uma mensagem como 'failed' e armazena o motivo."""
        self._update_message_status(message_id, "failed", reason)