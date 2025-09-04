from bson import ObjectId
from datetime import datetime

class MessageDAO:
    def __init__(self, db_client, config: dict):
        self.db = db_client[config["db_name"]]
        # Coleção principal para guardar o histórico da conversa (usuário e IA)
        self.collection_messages = self.db[config["collection_messages"]]

    def insert_message(self, message_data: dict):
        """
        Insere uma nova mensagem (de qualquer autor) na coleção de mensagens.
        Garante que os campos 'created_at' e 'role' existam.
        """
        if "created_at" not in message_data:
            message_data["created_at"] = datetime.utcnow()
        if "role" not in message_data:
            # Define 'user' como padrão se o role não for especificado
            message_data["role"] = "user"
            
        return self.collection_messages.insert_one(message_data)

    def get_history_by_user(self, user_id: str, limit=10):
        """
        Busca o histórico de um usuário, ordenado do mais antigo para o mais novo.
        (Este método será útil para a próxima fase do seu projeto)
        """
        return list(self.collection_messages.find(
            {"from": user_id}
        ).sort("created_at", 1).limit(limit))