import pika
import json

def load_config():
    with open("config/config.json", "r") as f:
        return json.load(f)

def get_rabbit_connection():
    config = load_config()["rabbitmq"]
    credentials = pika.PlainCredentials(config["user"], config["password"])
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=config["host"], credentials=credentials)
    )
    return connection, config