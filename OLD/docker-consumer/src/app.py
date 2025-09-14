# app.py
from src.consumer.rabbitmq_consumer import start_consumer
from src.utils.logger import get_logger
from src.config import settings # Importa as configurações centralizadas

logger = get_logger("app_consumer")

def main():
    """
    Função principal que inicia um único processo consumidor.
    """
    try:
        # Passa o objeto de configurações do RabbitMQ diretamente.
        # .model_dump() converte o objeto Pydantic para um dicionário, se necessário.
        rabbit_config = settings.rabbitmq.model_dump()
        logger.info("Configurações carregadas. Iniciando consumidor...", extra=rabbit_config)
        start_consumer(rabbit_config)

    except Exception as e:
        logger.critical("Erro inesperado e fatal na aplicação. Encerrando.", extra={'error': str(e)})
        exit(1)

if __name__ == "__main__":
    main()