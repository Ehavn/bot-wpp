import pika
import json
import os
import time
from pika.exceptions import AMQPConnectionError

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.json')
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("ERRO: O arquivo 'config/config.json' não foi encontrado.")

def get_rabbit_connection():
    config = load_config()
    rabbit_config = config.get("rabbitmq", {})
    
    host = os.getenv("RABBIT_HOST", rabbit_config.get("host", "localhost"))
    user = os.getenv("RABBIT_USER", rabbit_config.get("user"))
    password = os.getenv("RABBIT_PASSWORD", rabbit_config.get("password"))
    
    if not user or not password:
        raise ValueError("Credenciais do RabbitMQ não definidas.")

    credentials = pika.PlainCredentials(user, password)
    parameters = pika.ConnectionParameters(host=host, credentials=credentials, connection_attempts=5, retry_delay=5)

    max_retries = 5
    last_exception = None
    for attempt in range(max_retries):
        try:
            connection = pika.BlockingConnection(parameters)
            print("Conexão com RabbitMQ estabelecida com sucesso.")
            return connection, rabbit_config
        except AMQPConnectionError as e:
            last_exception = e
            wait_time = 2 ** attempt
            print(f"Falha ao conectar ao RabbitMQ (tentativa {attempt + 1}/{max_retries}). Tentando novamente em {wait_time} segundos... Erro: {e}")
            time.sleep(wait_time)

    raise AMQPConnectionError(f"Não foi possível conectar ao RabbitMQ após {max_retries} tentativas.") from last_exception

def setup_queues(channel, config):
    dlx_exchange_name = 'dlx_exchange'
    dead_letter_queue_name = 'dead_letter_queue'
    channel.exchange_declare(exchange=dlx_exchange_name, exchange_type='fanout')
    channel.queue_declare(queue=dead_letter_queue_name, durable=True)
    channel.queue_bind(exchange=dlx_exchange_name, queue=dead_letter_queue_name)
    queue_args = {"x-dead-letter-exchange": dlx_exchange_name}
    channel.queue_declare(queue=config["queue_new_messages"], durable=True, arguments=queue_args)
    channel.queue_declare(queue=config["queue_ia_messages"], durable=True, arguments=queue_args)
    print("Filas e Dead Letter Exchange verificadas/criadas com sucesso.")