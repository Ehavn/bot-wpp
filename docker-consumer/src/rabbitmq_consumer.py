import pika
import json
import time
from .mongo_client import get_mongo_client
from .logger import get_logger

logger = get_logger("consumer")

def start_consumer(rabbit_config):
    RABBIT_HOST = rabbit_config["host"]
    RABBIT_USER = rabbit_config["user"]
    RABBIT_PASS = rabbit_config["password"]
    QUEUE_NAME = rabbit_config["queue"]

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
            msg["created_at"] = datetime.utcnow()  # timestamp em UTC

            # msg["created_at"] = datetime.utcnow()  # alternativa de nome
            collection_raw.insert_one(msg)
            logger.info("Mensagem inserida no MongoDB com status 'pending'!")

        except Exception as e:
            logger.error(f"Erro ao inserir no MongoDB: {e}")
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
    logger.info("Consumidor iniciado, aguardando mensagens...")
    channel.start_consuming()
