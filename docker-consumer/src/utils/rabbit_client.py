# Arquivo: src/utils/rabbit_client.py (Refatorado e Padronizado)
import pika
import time
from pika.exceptions import AMQPConnectionError
from src.config import config # Usa a configuração central

def get_rabbit_connection():
    max_retries = 5
    last_exception = None
    for attempt in range(max_retries):
        try:
            # Usa os atributos padronizados do objeto config
            credentials = pika.PlainCredentials(config.RABBITMQ_USER, config.RABBITMQ_PASSWORD)
            parameters = pika.ConnectionParameters(
                host=config.RABBITMQ_HOST,
                credentials=credentials,
                connection_attempts=5,
                retry_delay=5
            )
            connection = pika.BlockingConnection(parameters)
            print(f"Conexão com RabbitMQ estabelecida com sucesso em '{config.RABBITMQ_HOST}'.")
            
            # Retorna um dicionário simples com os nomes das filas
            rabbit_config_dict = {
                "queue_new_messages": config.RABBITMQ_QUEUE_NEW,
                "queue_ia_messages": config.RABBITMQ_QUEUE_IA
            }
            return connection, rabbit_config_dict
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
    
    # Usa as chaves corretas do dicionário de configuração
    channel.queue_declare(queue=config["queue_new_messages"], durable=True, arguments=queue_args)
    channel.queue_declare(queue=config["queue_ia_messages"], durable=True, arguments=queue_args)
    print("Filas e Dead Letter Exchange verificadas/criadas com sucesso.")