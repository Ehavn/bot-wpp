import json
from src.consumer.rabbitmq_consumer import start_consumer
from src.utils.logger import get_logger

logger = get_logger("app")

if __name__ == "__main__":
    with open("./config/config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    rabbit_config = config["rabbitmq"]
    
    logger.info("Iniciando consumidor...")
    
    start_consumer(rabbit_config)