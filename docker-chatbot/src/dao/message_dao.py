# Arquivo: src/dao/message_dao.py

from bson import ObjectId
from datetime import datetime

class MessageDAO:
    def __init__(self, db_client, config: dict):
        self.db = db_client[config["db_name"]]
        self.collection_messages = self.db[config["collection_messages"]]

    def insert_message(self, message_data: dict):
        """
        Insere uma nova mensagem (de qualquer autor) na coleção de mensagens.
        """
        if "created_at" not in message_data:
            message_data["created_at"] = datetime.utcnow()
        if "role" not in message_data:
            message_data["role"] = "user"
            
        return self.collection_messages.insert_one(message_data)

    # --- MÉTODO CORRIGIDO ---
    def get_history_by_conversation(self, conversation_id: str, limit=20):
        """
        Busca o histórico completo de uma conversa (usuário e IA) pelo ID da conversa,
        ordenado do mais antigo para o mais novo.
        """
        return list(self.collection_messages.find(
            {"conversationId": conversation_id}
        ).sort("created_at", 1).limit(limit))