# Arquivo: src/consumer/rabbitmq_consumer.py (exemplo baseado no seu erro)

import pika
import json
import logging

# Supondo que você tenha funções para conectar ao Mongo e processar a mensagem
# from src.db.mongo_client import get_mongo_connection
# from src.services.message_processor import process_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def callback(ch, method, properties, body):
    """Função chamada quando uma mensagem é recebida."""
    logger.info("Mensagem recebida, processando...")
    try:
        message_data = json.loads(body)
        # Aqui você chamaria sua lógica para salvar no MongoDB
        # Exemplo: process_message(message_data)
        print(message_data) # Apenas para exemplo
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info("Mensagem processada e confirmada (ack).")
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def start_consumer(config):
    """Inicia o consumidor e trata o desligamento gracioso."""
    connection = None  # Inicializa a variável de conexão
    try:
        # Estabelece a conexão
        credentials = pika.PlainCredentials(config['user'], config['password'])
        parameters = pika.ConnectionParameters(host=config['host'], credentials=credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        channel.queue_declare(queue=config['queue'], durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=config['queue'], on_message_callback=callback)

        logger.info("Consumidor iniciado, aguardando mensagens...")
        # --- PONTO PRINCIPAL DA MUDANÇA ---
        # O loop de consumo agora está dentro de um bloco try...except
        channel.start_consuming()

    except KeyboardInterrupt:
        logger.info("Interrupção recebida (Ctrl+C). Encerrando o consumidor...")
        # Para o loop de consumo de forma segura
        if 'channel' in locals() and channel.is_open:
            channel.stop_consuming()

    except Exception as e:
        logger.error(f"Ocorreu um erro inesperado no consumidor: {e}")

    finally:
        # Garante que a conexão seja fechada, não importa o que aconteça
        if connection and connection.is_open:
            connection.close()
            logger.info("Conexão com o RabbitMQ fechada.")
        logger.info("Consumidor encerrado.")

# Supondo que seu app.py do consumidor chame esta função
# if __name__ == '__main__':
#     # Carrega config do rabbit...
#     start_consumer(rabbit_config)