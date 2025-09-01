import json
from datetime import datetime
from src.utils.logger import get_logger
from src.utils.mongo_client import get_mongo_client
from src.utils.rabbit_client import get_rabbit_connection

logger = get_logger("error_consumer")

def start_error_consumer():
    # Conexões
    mongo_client, mongo_config = get_mongo_client()
    rabbit_connection, rabbit_config = get_rabbit_connection()

    # Acessa a coleção de erros
    db = mongo_client[mongo_config["db_name"]]
    collection_dead_letter = db[mongo_config["collection_dead_letter"]]
    
    channel = rabbit_connection.channel()
    queue_error = rabbit_config["queue_error"]
    channel.queue_declare(queue=queue_error, durable=True)
    logger.info(f"Conectado e escutando a fila de erros: '{queue_error}'")

    def error_callback(ch, method, properties, body):
        try:
            failed_message = json.loads(body)
            logger.warning(f"Mensagem de erro recebida: {failed_message}")

            error_document = {
                "original_message": failed_message,
                "failed_at": datetime.utcnow(),
                "status": "unresolved",
                "retry_count": 0
            }
            collection_dead_letter.insert_one(error_document)
            logger.info("Mensagem de erro persistida no MongoDB para análise.")
        except Exception as e:
            logger.critical(f"Falha ao processar a fila de erro: {e}. A mensagem pode ser perdida.")
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=queue_error, on_message_callback=error_callback)
    channel.start_consuming()