import pika
import json
import os
import logging

logger = logging.getLogger(__name__)

try:
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config/config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    rabbit_config = config['rabbitmq']

    RABBIT_HOST = rabbit_config.get("host", "localhost")
    RABBIT_USER = rabbit_config.get("user", "user")
    RABBIT_PASS = rabbit_config.get("password", "password")
    QUEUE_NAME = rabbit_config.get("queue", "whatsapp_queue")
    
except FileNotFoundError:
    logger.error("ERRO: O arquivo 'config.json' não foi encontrado na raiz do projeto.")
    # Se o arquivo de configuração não for encontrado, podemos parar a aplicação ou usar padrões.
    # Por segurança, vamos definir valores que provavelmente falharão para forçar a correção.
    RABBIT_HOST, RABBIT_USER, RABBIT_PASS, QUEUE_NAME = None, None, None, None
except KeyError:
    logger.error("ERRO: A chave 'rabbitmq' ou uma de suas subchaves não foi encontrada no 'config.json'.")
    RABBIT_HOST, RABBIT_USER, RABBIT_PASS, QUEUE_NAME = None, None, None, None


# --- FIM DA MODIFICAÇÃO ---


def publish_message(msg: dict):
    """Publica uma mensagem no RabbitMQ"""
    # Esta função não precisa de nenhuma alteração, pois já usa as variáveis acima.
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