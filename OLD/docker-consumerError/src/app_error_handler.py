from src.consumers.error_consumer import start_error_consumer
from src.utils.logger import get_logger

logger = get_logger("error_app")

if __name__ == "__main__":
    logger.info("Iniciando consumidor da fila de erros...")
    try:
        start_error_consumer()
    except KeyboardInterrupt:
        logger.info("Consumidor de erros encerrado.")
    except Exception as e:
        logger.critical(f"Erro fatal no consumidor de erros: {e}", exc_info=True)