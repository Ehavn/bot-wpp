# Arquivo: src/utils/rabbit_client.py
import pika
import json
import os

def load_config(config_file="config/config.json"):
    """
    Carrega o arquivo de configuração de forma segura, calculando o 
    caminho a partir da raiz do projeto.
    """
    try:
        path = os.path.join(os.path.dirname(__file__), '..', '..', config_file)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"ERRO: O arquivo '{config_file}' não foi encontrado.")

def get_rabbit_connection():
    """
    Carrega a configuração do RabbitMQ e estabelece uma conexão autenticada.
    """
    config = load_config()
    rabbit_config = config.get("rabbitmq")
    if not rabbit_config:
        raise ValueError("Chave 'rabbitmq' não encontrada no config.json")

    credentials = pika.PlainCredentials(rabbit_config['user'], rabbit_config['password'])
    parameters = pika.ConnectionParameters(
        host=rabbit_config.get("host", "localhost"),
        credentials=credentials
    )
    
    connection = pika.BlockingConnection(parameters)
    return connection, rabbit_config

# --- FUNÇÃO CORRIGIDA ---
def setup_queues(channel, config):
    """Garante que a fila principal do RabbitMQ, definida no config, existe."""
    if "queue" in config:
        queue_name = config["queue"]
        channel.queue_declare(queue=queue_name, durable=True)
        print(f"Fila '{queue_name}' verificada/criada.")
    else:
        raise ValueError("A chave 'queue' para o RabbitMQ não está definida no config.json")