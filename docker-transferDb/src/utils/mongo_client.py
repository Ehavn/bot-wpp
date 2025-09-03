# Arquivo: src/utils/mongo_client.py

import json
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def load_config():
    """
    Carrega o arquivo de configuração de forma segura.
    """
    try:
        # Calcula o caminho para o config.json na raiz do projeto
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.json')
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("ERRO: O arquivo 'config/config.json' não foi encontrado na raiz do projeto.")

def get_mongo_client():
    """
    Cria e retorna um cliente do MongoDB e a sua configuração específica.
    """
    config = load_config()
    mongo_config = config.get("mongo")
    if not mongo_config:
        raise ValueError("Chave 'mongo' não encontrada no config.json")
    
    connection_uri = mongo_config.get("connectionUri")
    if not connection_uri:
        raise ValueError("Chave 'connectionUri' não encontrada na seção 'mongo' do config")
    
    try:
        client = MongoClient(connection_uri)
        # Testa a conexão para garantir que está funcionando
        client.admin.command('ping')
        return client, mongo_config
    except ConnectionFailure as e:
        print(f"Falha ao conectar ao MongoDB: {e}")
        raise