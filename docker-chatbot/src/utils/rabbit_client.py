import os
import pika

def get_rabbit_connection():
    rabbit_config = {
        "host": os.getenv("RABBITMQ_HOST", "localhost"),
        "user": os.getenv("RABBITMQ_USER"),
        "password": os.getenv("RABBITMQ_PASSWORD"),
        "queue": os.getenv("RABBITMQ_QUEUE")
    }
    if not all([rabbit_config["user"], rabbit_config["password"], rabbit_config["queue"]]):
        raise ValueError("Variáveis de ambiente do RabbitMQ (USER, PASSWORD, QUEUE) não definidas.")
    credentials = pika.PlainCredentials(rabbit_config['user'], rabbit_config['password'])
    parameters = pika.ConnectionParameters(host=rabbit_config["host"], credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    return connection, rabbit_config

def setup_queues(channel, config):
    """
    Garante que a fila principal, a Dead-Letter Exchange (DLX) e a Dead-Letter Queue (DLQ)
    existam e estejam corretamente vinculadas.
    """
    main_queue = config["queue"]
    dlx_name = "dlx_exchange"
    dlq_name = f"{main_queue}-dlq"

    # Declara o exchange para mensagens mortas (DLX)
    channel.exchange_declare(exchange=dlx_name, exchange_type='fanout', durable=False)
    
    # Declara a fila de mensagens mortas (DLQ)
    channel.queue_declare(queue=dlq_name, durable=True)
    
    # Vincula a DLQ ao DLX
    channel.queue_bind(queue=dlq_name, exchange=dlx_name, routing_key='')

    # Declara a fila principal, configurando-a para enviar mensagens mortas ao DLX
    args = {
        "x-dead-letter-exchange": dlx_name
    }
    
    channel.queue_declare(queue=main_queue, durable=True, arguments=args)
    
    print(f"✅ Fila principal '{main_queue}' e DLQ '{dlq_name}' configuradas com sucesso.")