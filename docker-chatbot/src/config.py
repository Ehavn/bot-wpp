from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Carrega variáveis de um arquivo .env
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # Personalidade do AI
    AI_NAME: str = "Assistente"
    AI_SYSTEM_PROMPT: str = "Você é um assistente virtual."

    # Gemini
    GEMINI_API_KEY: str

    # WhatsApp
    WHATSAPP_TOKEN: str
    WHATSAPP_PHONE_NUMBER_ID: str

    # RabbitMQ
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_QUEUE: str

    # MongoDB
    MONGO_URI: str
    MONGO_DB_NAME: str = "messages"
    MONGO_COLLECTION_MESSAGES: str = "raw"
    
    # Aplicação
    PDFS_PATH: str = "documents/pdfs"
    LOG_LEVEL: str = "INFO"

# Instância única que será importada em todo o projeto
settings = Settings()