import json
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def load_mongo_config():
    """
    Carrega a seção 'mongo' do config.json de forma segura,
    calculando o caminho a partir da localização deste script.
    """
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.json')
        
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        return config["mongo"]

    except FileNotFoundError:
        # logger.critical("ERRO: 'config/config.json' não foi encontrado.")
        raise  # Re-lança a exceção para interromper a execução
    except KeyError:
        # logger.critical("ERRO: A chave 'mongo' não foi encontrada no config.json.")
        raise

def get_mongo_client():
    """
    Cria e retorna um cliente do MongoDB e sua configuração.
    """
    config = load_mongo_config()
    connection_uri = config.get("connectionUri")
    if not connection_uri:
        raise ValueError("'connectionUri' não encontrado na configuração do MongoDB.")

    try:
        client = MongoClient(connection_uri)
        # 2. Testa a conexão para garantir que está funcionando antes de continuar
        client.admin.command('ping')
        # logger.info("Conexão com MongoDB estabelecida com sucesso.")
        return client, config
    except ConnectionFailure as e:
        # logger.critical(f"Falha ao conectar ao MongoDB: {e}")
        raise