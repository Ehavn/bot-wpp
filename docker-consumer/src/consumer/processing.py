# src/consumer/processing.py
import json
from pymongo.collection import Collection
from datetime import datetime
from typing import Dict, Any

class MessageProcessor:
    """
    Encapsula toda a lógica de negócio para processar uma mensagem.
    Esta classe não sabe nada sobre RabbitMQ; apenas sobre dados.
    """
    def __init__(self, mongo_collection: Collection):
        """
        Recebe a coleção do MongoDB como uma dependência (Injeção de Dependência).
        """
        self.mongo_collection = mongo_collection

    def execute(self, body: bytes) -> str:
        """
        Orquestra o processo de transformação e armazenamento da mensagem.
        Retorna o ID do documento inserido.
        """
        transformed_data = self._transform_data(body)
        inserted_id = self._insert_to_mongodb(transformed_data)
        return inserted_id

    def _transform_data(self, body: bytes) -> Dict[str, Any]:
        """
        Aplica a lógica de negócio para transformar os dados da mensagem.
        """
        message_data = json.loads(body)
        message_data['status'] = 'processed'
        message_data['role'] = 'user'
        message_data['timestamp_insert'] = datetime.now().isoformat()
        return message_data

    def _insert_to_mongodb(self, data: Dict[str, Any]) -> str:
        """
        Persiste os dados transformados no banco de dados.
        """
        result = self.mongo_collection.insert_one(data)
        return str(result.inserted_id)