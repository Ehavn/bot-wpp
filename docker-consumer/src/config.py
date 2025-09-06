import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel

# Garante que o .env seja lido. O Pydantic-Settings fará isso automaticamente
# se python-dotenv estiver instalado, mas podemos ser explícitos.
from dotenv import load_dotenv
load_dotenv()

class RabbitMQSettings(BaseModel):
    """Configurações específicas do RabbitMQ."""
    host: str = os.getenv("RABBIT_HOST", "localhost")
    user: str = os.getenv("RABBIT_USER", "guest")
    password: str = os.getenv("RABBIT_PASS", "guest")
    queue: str = os.getenv("RABBIT_QUEUE_MESSAGES", "new_messages")
    queue_error: str = os.getenv("RABBIT_QUEUE_ERROR", "failed_messages")

class MongoSettings(BaseModel):
    """Configurações específicas do MongoDB."""
    connection_uri: str = os.getenv("MONGO_CONNECTION_URI")
    db_name: str = os.getenv("MONGO_DB_NAME", "messages")
    collection_messages: str = os.getenv("MONGO_COLLECTION_MESSAGES", "raw")


class AppSettings(BaseSettings):
    """
    Classe principal que carrega todas as configurações da aplicação.
    Ela automaticamente buscará variáveis de ambiente correspondentes.
    """
    rabbitmq: RabbitMQSettings = RabbitMQSettings()
    mongo: MongoSettings = MongoSettings()
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_nested_delimiter='__'
    )

# Instância única que será importada em toda a aplicação.
# O Pydantic garante que, se uma variável obrigatória (ex: MONGO_CONNECTION_URI)
# não for encontrada, a aplicação falhará ao iniciar com um erro claro.
settings = AppSettings()