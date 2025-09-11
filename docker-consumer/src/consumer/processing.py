# src/consumer/processing.py
import json
from pymongo.collection import Collection
from datetime import datetime
from typing import Dict, Any

class MessageProcessor:
    """
    Encapsula toda a lógica de negócio para processar uma mensagem.
    """
    def __init__(self, mongo_collection: Collection):
        """
        Recebe a coleção do MongoDB como uma dependência.
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
        loaded_data = json.loads(body)
        
        # --- INÍCIO DA CORREÇÃO ---
        # Verifica se o dado carregado é uma lista. Se for, pega o primeiro elemento.
        if isinstance(loaded_data, list) and loaded_data:
            message_data = loaded_data[0]
        else:
            message_data = loaded_data
        # --- FIM DA CORREÇÃO ---

        # Garante que temos um dicionário antes de continuar
        if not isinstance(message_data, dict):
            raise TypeError("O corpo da mensagem, após o processamento, não é um dicionário.")

        message_data['status'] = 'pending'
        message_data['role'] = 'user'
        message_data['timestamp_insert'] = datetime.now().isoformat()
        return message_data

    def _insert_to_mongodb(self, data: Dict[str, Any]) -> str:
        """
        Persiste os dados transformados no banco de dados.
        """
        result = self.mongo_collection.insert_one(data)
        return str(result.inserted_id)