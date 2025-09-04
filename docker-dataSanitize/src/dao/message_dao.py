# Arquivo: src/dao/message_dao.py

from bson import ObjectId

class MessageDAO:
    def __init__(self, db_client, config: dict):
        self.db = db_client[config["db_name"]]
        # Usaremos a coleção 'raw' como o local unificado para todas as mensagens
        self.collection_messages = self.db[config["collection_raw"]]

    def save_raw_message(self, message_data: dict) -> ObjectId:
        """Salva a mensagem original com status inicial 'pending'."""
        message_data['status'] = 'pending'
        result = self.collection_messages.insert_one(message_data)
        return result.inserted_id

    def find_and_update_one_pending_message(self):
        """Encontra uma mensagem com status 'pending' e a atualiza para 'processing'."""
        return self.collection_messages.find_one_and_update(
            {'status': 'pending'},
            {'$set': {'status': 'processing'}}
        )

    def mark_message_as_processed(self, message_id: ObjectId):
        """Atualiza o status de uma mensagem para 'processed'."""
        self.collection_messages.update_one(
            {'_id': message_id},
            {'$set': {'status': 'processed'}}
        )
    
    def mark_message_as_failed(self, message_id: ObjectId):
        """Atualiza o status de uma mensagem para 'failed'."""
        self.collection_messages.update_one(
            {'_id': message_id},
            {'$set': {'status': 'failed'}}
        )

    def get_history_by_conversation_id(self, conversation_id: str, limit: int = 20) -> list:
        """
        Busca as últimas 'limit' mensagens de uma conversa (usuário e IA),
        e retorna em ordem cronológica (crescente).
        """
        # O filtro agora busca pelo 'conversationId', que une todas as mensagens
        # da mesma conversa, independentemente de quem enviou ('from').
        cursor = self.collection_messages.find(
            {"conversationId": conversation_id, "status": "processed"} 
        # A ordenação é feita por 'created_at' e descendente (-1) para pegar
        # as mensagens MAIS RECENTES primeiro.
        ).sort("created_at", -1).limit(limit)
        
        history = []
        for doc in cursor:
            # Converte o ObjectId para string para ser serializável em JSON
            doc["_id"] = str(doc["_id"])
            history.append(doc)
            
        # A lista é invertida aqui para que a ordem final seja crescente (cronológica),
        # que é o formato que a IA espera (do mais antigo para o mais novo).
        history.reverse()