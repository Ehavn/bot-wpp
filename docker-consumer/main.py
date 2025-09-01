import pika
import json
import time
from utils.mongo_client import get_mongo_client
from utils.logger import get_logger

logger = get_logger("consumer")

# Carrega configuração do RabbitMQ
with open("config/config.json") as f:
    config = json.load(f)

RABBIT_HOST = config["rabbitmq"]["host"]
RABBIT_USER = config["rabbitmq"]["user"]
RABBIT_PASS = config["rabbitmq"]["password"]
QUEUE_NAME = config["rabbitmq"]["queue"]

# Conexão com MongoDB Atlas
mongo_client, mongo_config = get_mongo_client()
db = mongo_client[mongo_config["db_name"]]
collection_raw = db[mongo_config["collection_raw"]]

logger.info("Conexão com MongoDB Atlas estabelecida!")

# Conexão com RabbitMQ
credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
parameters = pika.ConnectionParameters(host=RABBIT_HOST, credentials=credentials)

# Tenta conectar até RabbitMQ ficar pronto
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

# Callback para processar mensagens
def callback(ch, method, properties, body):
    try:
        msg = json.loads(body)
        logger.info(f"Mensagem recebida: {msg}")

        # Adiciona status "pending"
        msg["status"] = "pending"

        # Salva mensagem diretamente na coleção raw
        collection_raw.insert_one(msg)
        logger.info("Mensagem inserida no MongoDB Atlas com status pending!")

    except Exception as e:
        logger.error(f"Erro ao inserir no MongoDB: {e}")

    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)

# Inicia consumidor
channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

logger.info("Consumidor iniciado, aguardando mensagens...")
channel.start_consuming()
