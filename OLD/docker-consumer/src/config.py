from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from src.utils.secrets import get_secret

# Caminho para o .env local
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE_PATH = BASE_DIR / ".env"

# -----------------------------
# Configurações RabbitMQ
# -----------------------------
class RabbitMQSettings(BaseSettings):
    host: str
    user: str
    password: str = Field(alias="RABBIT_PASS")
    queue_messages: str
    queue_error: str

    model_config = SettingsConfigDict(
        env_prefix="RABBIT_",
        env_file=str(ENV_FILE_PATH),
        extra="allow"  # Permite que variáveis do Mongo ou outras extras não quebrem
    )

# -----------------------------
# Configurações MongoDB
# -----------------------------
class MongoSettings(BaseSettings):
    connection_uri: str
    db_name: str
    collection_messages: str

    model_config = SettingsConfigDict(
        env_prefix="MONGO_",
        env_file=str(ENV_FILE_PATH),
        extra="allow"
    )

# -----------------------------
# Configurações da Aplicação
# -----------------------------
class AppSettings(BaseSettings):
    rabbitmq: RabbitMQSettings = RabbitMQSettings()
    mongo: MongoSettings = MongoSettings()

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        extra="allow"  # Evita erro se houver outras variáveis no .env
    )

# Instância global de configurações
settings = AppSettings()

# -----------------------------
# Sobrescreve com secrets em produção
# -----------------------------
try:
    if get_secret("ENVIRONMENT") == "production":
        # RabbitMQ
        settings.rabbitmq.user = get_secret("RABBIT_USER") or settings.rabbitmq.user
        settings.rabbitmq.password = get_secret("RABBIT_PASS") or settings.rabbitmq.password

        # MongoDB
        settings.mongo.connection_uri = get_secret("MONGO_CONNECTION_URI") or settings.mongo.connection_uri
except Exception:
    # Se não estiver em produção ou falhar o get_secret, mantém valores do .env
    pass
