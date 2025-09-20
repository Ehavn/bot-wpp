# src/dao/message_dao.py
from datetime import datetime

class MessageDAO:
    def __init__(self, db_client, config: dict):
        self.db = db_client[config["db_name"]]
        self.collection_messages = self.db[config["collection_messages"]]

    def insert_message(self, message_data: dict):
        """
        Insere uma nova mensagem na coleção.
        """
        if "created_at" not in message_data:
            message_data["created_at"] = datetime.utcnow()
        
        return self.collection_messages.insert_one(message_data)

    def get_history_by_conversation(self, conversation_id: str, limit: int = 20):
        """
        Busca o histórico de uma conversa, ordenado do mais antigo para o mais novo.
        """
        return list(self.collection_messages.find(
            {"conversationId": conversation_id}
        ).sort("created_at", 1).limit(limit))