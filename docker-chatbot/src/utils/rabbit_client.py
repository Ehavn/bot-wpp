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

def setup_queues_and_exchanges(channel, config):
    """
    Garante que a exchange principal (com capacidade de atraso) e as filas
    necessárias (principal e DLQ) existam e estejam vinculadas.
    """
    main_queue = config["queue"]
    dlq_name = f"{main_queue}-dlq"
    
    # Exchange para mensagens mortas (DLQ)
    dlx_name = "dlx_exchange"
    channel.exchange_declare(exchange=dlx_name, exchange_type='fanout', durable=False)
    channel.queue_declare(queue=dlq_name, durable=True)
    channel.queue_bind(queue=dlq_name, exchange=dlx_name)

    main_exchange = 'delayed_exchange'
    args = {"x-delayed-type": "direct"}
    
    channel.exchange_declare(
        exchange=main_exchange, 
        exchange_type='x-delayed-message', 
        durable=True, 
        auto_delete=False, 
        arguments=args
    )

    queue_args = {"x-dead-letter-exchange": dlx_name}
    channel.queue_declare(queue=main_queue, durable=True, arguments=queue_args)

    channel.queue_bind(queue=main_queue, exchange=main_exchange, routing_key=main_queue)
    
    print(f"✅ Exchange Atrasada '{main_exchange}' e Fila Principal '{main_queue}' configuradas com sucesso.")