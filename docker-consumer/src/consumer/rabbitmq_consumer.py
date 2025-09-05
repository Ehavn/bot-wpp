# src/consumer/rabbitmq_consumer.py

import pika
import json
import logging
import functools
from datetime import datetime  # <-- 1. IMPORTAR O MÓDULO DATETIME

# Importamos a sua função de conexão com o MongoDB
from src.utils.mongo_client import get_mongo_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- INÍCIO DA MUDANÇA ---
def callback(ch, method, properties, body, mongo_collection):
    """
    Função chamada quando uma mensagem é recebida.
    Enriquece a mensagem com status, role e timestamp antes de salvar.
    """
    logger.info("Mensagem recebida, processando para salvar no MongoDB...")
    try:
        # Decodifica a mensagem original do RabbitMQ
        message_data = json.loads(body)
        
        # --- 2. ADICIONANDO OS NOVOS CAMPOS ---
        # Adiciona os campos de status e role fixos
        message_data['status'] = 'pending'
        message_data['role'] = 'user'
        
        # Gera o timestamp no formato solicitado e o adiciona
        # Usamos .%f e fatiamos [:-3] para obter os milissegundos (3 dígitos)
        timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        message_data['timestamp_insert'] = timestamp_str

        # --- FIM DA LÓGICA DE ADIÇÃO ---
        
        # Insere o documento ENRIQUECIDO no MongoDB
        result = mongo_collection.insert_one(message_data)
        logger.info(f"Documento enriquecido inserido no MongoDB com o ID: {result.inserted_id}")
        
        # Confirma ao RabbitMQ que a mensagem foi processada com sucesso
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info("Mensagem processada e confirmada (ack).")

    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON da mensagem: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        logger.error(f"Erro ao enriquecer ou inserir a mensagem no MongoDB: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
# --- FIM DA MUDANÇA ---


def start_consumer(config):
    # O resto do arquivo permanece exatamente o mesmo de antes...
    mongo_client = None
    connection = None
    try:
        logger.info("Conectando ao MongoDB...")
        mongo_client, mongo_config = get_mongo_client()
        db = mongo_client[mongo_config["db_name"]]
        collection = db[mongo_config["collection_messages"]]
        logger.info("Conexão com MongoDB estabelecida com sucesso.")

        credentials = pika.PlainCredentials(config['user'], config['password'])
        parameters = pika.ConnectionParameters(host=config['host'], credentials=credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        channel.queue_declare(queue=config['queue'], durable=True)
        channel.basic_qos(prefetch_count=1)

        on_message_callback = functools.partial(callback, mongo_collection=collection)

        channel.basic_consume(
            queue=config['queue'],
            on_message_callback=on_message_callback
        )

        logger.info("Consumidor iniciado, aguardando mensagens...")
        channel.start_consuming()

    except KeyboardInterrupt:
        logger.info("Interrupção recebida (Ctrl+C). Encerrando o consumidor...")
        if 'channel' in locals() and channel.is_open:
            channel.stop_consuming()
    except Exception as e:
        logger.error(f"Ocorreu um erro crítico no consumidor: {e}")
    finally:
        if connection and connection.is_open:
            connection.close()
            logger.info("Conexão com o RabbitMQ fechada.")
        if mongo_client:
            mongo_client.close()
            logger.info("Conexão com o MongoDB fechada.")
        logger.info("Consumidor encerrado.")