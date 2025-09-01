# src/utils/rabbit_client.py
import pika
import json

def load_config():
    with open("config/config.json", "r") as f:
        return json.load(f)

def get_rabbit_connection():
    config = load_config()
    rabbit_config = config.get("rabbitmq", {})
    
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbit_config.get("host", "localhost"))
    )
    return connection, rabbit_config.get("rabbitmq", {})

def setup_queues(channel, config):
    """Garante que as filas do RabbitMQ existem."""
    channel.queue_declare(queue=config["queue_new_messages"], durable=True)
    channel.queue_declare(queue=config["queue_ia_messages"], durable=True)
    print("Filas do RabbitMQ verificadas/criadas.")