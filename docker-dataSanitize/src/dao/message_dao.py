# src/dao/message_dao.py
from bson import ObjectId

class MessageDAO:
    def __init__(self, db_client, config: dict):
        self.db = db_client[config["db_name"]]
        self.collection_raw = self.db[config["collection_raw"]]

    def save_raw_message(self, message_data: dict) -> ObjectId:
        """
        Salva a mensagem original e retorna o ID do MongoDB.
        """
        result = self.collection_raw.insert_one(message_data)
        return result.inserted_id

    def get_message_history_by_phone(self, phone_number: str, limit: int = 10) -> list:
        """
        Busca as últimas 'limit' mensagens de um número de telefone,
        excluindo a mais recente (que é a mensagem atual).
        """
        # Ordena por timestamp descendente para pegar as mais recentes
        cursor = self.collection_raw.find(
            {"phone_number": phone_number}
        ).sort("timestamp", -1).limit(limit)
        
        # Converte o cursor para lista e remove o ObjectId para serialização
        history = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            history.append(doc)
            
        return history