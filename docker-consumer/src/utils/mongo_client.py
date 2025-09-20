import time
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from src.config import config  # Importa a configuração centralizada

def get_mongo_client():
    """
    Cria e retorna um cliente do MongoDB usando a configuração centralizada.
    Inclui lógica de retentativas.
    """
    max_retries = 5
    last_exception = None
    for attempt in range(max_retries):
        try:
            client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            print("Conexão com MongoDB estabelecida com sucesso.")
            mongo_config = {
                "db_name": config.MONGO_DB_NAME,
                "collection_raw": config.MONGO_COLLECTION_RAW
            }
            return client, mongo_config
        except ConnectionFailure as e:
            last_exception = e
            wait_time = 2 ** attempt
            print(f"Falha ao conectar ao MongoDB (tentativa {attempt + 1}/{max_retries}). Tentando novamente em {wait_time} segundos... Erro: {e}")
            time.sleep(wait_time)
            
    raise ConnectionFailure(f"Não foi possível conectar ao MongoDB após {max_retries} tentativas.") from last_exception