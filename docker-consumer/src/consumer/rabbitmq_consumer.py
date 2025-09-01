import pika
import json
import time
from datetime import datetime
from ..utils.mongo_client import get_mongo_client
from ..utils.logger import get_logger

logger = get_logger("consumer")

def start_consumer(rabbit_config):
    RABBIT_HOST = rabbit_config["host"]
    RABBIT_USER = rabbit_config["user"]
    RABBIT_PASS = rabbit_config["password"]
    QUEUE_NAME = rabbit_config["queue"]
    QUEUE_ERROR = rabbit_config.get("queue_error", "failed_messages")  # fila de erro

    # Conexão com MongoDB
    mongo_client, mongo_config = get_mongo_client()
    db = mongo_client[mongo_config["db_name"]]
    collection_raw = db[mongo_config["collection_raw"]]
    logger.info("Conexão com MongoDB Atlas estabelecida!")

    # Conexão com RabbitMQ
    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
    parameters = pika.ConnectionParameters(host=RABBIT_HOST, credentials=credentials)

    while True:
        try:
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            channel.queue_declare(queue=QUEUE_ERROR, durable=True)
            break
        except Exception as e:
            logger.warning(f"Aguardando RabbitMQ... {e}")
            time.sleep(5)

    logger.info("Conexão com RabbitMQ estabelecida!")

    # Callback
    def callback(ch, method, properties, body):
        try:
            msg = json.loads(body)
            logger.info(f"Mensagem recebida: {msg}")

            # Adiciona status e timestamp
            msg["status"] = "pending"
            msg["created_at"] = datetime.utcnow()

            collection_raw.insert_one(msg)
            logger.info("Mensagem inserida no MongoDB com status 'pending'!")

        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            # Reenvia mensagem para a fila de erro
            try:
                channel.basic_publish(
                    exchange="",
                    routing_key=QUEUE_ERROR,
                    body=body,
                    properties=pika.BasicProperties(delivery_mode=2)  # persistente
                )
                logger.warning("Mensagem redirecionada para a fila de erro!")
            except Exception as publish_err:
                logger.critical(f"Falha ao redirecionar para fila de erro: {publish_err}")

        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
    logger.info("Consumidor iniciado, aguardando mensagens...")
    channel.start_consuming()
