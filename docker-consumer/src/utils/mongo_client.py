# src/utils/mongo_client.py
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from .logger import get_logger
from ..config import settings # Importa as configurações centralizadas

logger = get_logger(__name__)

def get_mongo_client():
    """
    Cria e retorna um cliente do MongoDB usando as configurações centralizadas.
    """
    try:
        # A validação da URI já foi feita pelo Pydantic ao iniciar a app.
        client = MongoClient(settings.mongo.connection_uri)
        client.admin.command('ping') 
        logger.info("Conexão com MongoDB estabelecida com sucesso.")
        
        # Retorna o cliente e um dicionário com as configurações do Mongo.
        return client, settings.mongo.model_dump()
        
    except ConnectionFailure as e:
        logger.critical("Falha ao conectar ao MongoDB.", extra={'error': str(e)})
        raise