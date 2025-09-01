import pika
import json
import os
import logging

logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente (com valores padrão para desenvolvimento)
RABBIT_HOST = os.getenv("RABBIT_HOST", "localhost")
RABBIT_USER = os.getenv("RABBIT_USER", "guest")
RABBIT_PASS = os.getenv("RABBIT_PASS", "guest")
QUEUE_NAME = os.getenv("RABBIT_QUEUE", "whatsapp_queue")


def publish_message(msg: dict):
    """Publica uma mensagem no RabbitMQ"""
    try:
        credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
        parameters = pika.ConnectionParameters(host=RABBIT_HOST, credentials=credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)

        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=json.dumps(msg),
            properties=pika.BasicProperties(delivery_mode=2)  # persistente
        )
        logger.info("Mensagem publicada com sucesso no RabbitMQ")
        connection.close()

    except Exception as e:
        logger.error(f"Erro ao publicar mensagem no RabbitMQ: {e}")
        raise