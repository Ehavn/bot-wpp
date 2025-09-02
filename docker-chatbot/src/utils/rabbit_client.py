# src/utils/rabbit_client.py
import pika
import json
import os

def load_config():
    """
    Carrega o arquivo de configuração de forma segura, calculando o 
    caminho a partir da localização deste script.
    """
    try:
        # 1. Caminho robusto para o arquivo de configuração
        # (Sobe dois níveis a partir de 'src/utils/')
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.json')
        
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
            
    except FileNotFoundError:
        raise FileNotFoundError("ERRO: A pasta/arquivo 'config/config.json' não foi encontrado na raiz do projeto.")
    
def get_rabbit_connection():
    """
    Carrega a configuração do RabbitMQ e estabelece uma conexão autenticada.
    """
    config = load_config()
    rabbit_config = config.get("rabbitmq")
    if not rabbit_config:
        raise ValueError("Chave 'rabbitmq' não encontrada no config.json")

    # 2. Adiciona credenciais para uma conexão mais completa
    credentials = pika.PlainCredentials(rabbit_config['user'], rabbit_config['password'])
    parameters = pika.ConnectionParameters(
        host=rabbit_config.get("host", "localhost"),
        credentials=credentials
    )
    
    connection = pika.BlockingConnection(parameters)
    
    # 3. Retorna a configuração correta
    return connection, rabbit_config

def setup_queues(channel, config):
    """Garante que as filas do RabbitMQ existem."""
    # O código aqui estava correto e não precisou de alterações.
    channel.queue_declare(queue=config["queue_new_messages"], durable=True)
    channel.queue_declare(queue=config["queue_ia_messages"], durable=True)
    print("Filas do RabbitMQ verificadas/criadas.")