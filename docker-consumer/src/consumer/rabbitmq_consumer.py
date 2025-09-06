# src/consumer/rabbitmq_consumer.py
import pika
import json
import functools
import time
import signal
from ..utils.logger import get_logger
from ..utils.mongo_client import get_mongo_client
from .processing import MessageProcessor # Importa a nova classe de lógica de negócio

# Type hinting
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties
from pymongo.collection import Collection
from pymongo.mongo_client import MongoClient
from typing import Dict, Any

logger = get_logger(__name__)

class GracefulKiller:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        logger.info("Sinal de encerramento recebido. Finalizando o consumidor...")
        self.kill_now = True

def callback(
    ch: BlockingChannel, 
    method: Basic.Deliver, 
    properties: BasicProperties, 
    body: bytes, 
    mongo_collection: Collection
) -> None:
    logger.info("Mensagem recebida", extra={'delivery_tag': method.delivery_tag})
    try:
        # 1. Instancia o processador, injetando a dependência
        processor = MessageProcessor(mongo_collection=mongo_collection)
        # 2. Delega TODA a lógica de negócio para o processador
        inserted_id = processor.execute(body)
        
        logger.info("Mensagem processada e inserida com sucesso", extra={'inserted_id': inserted_id})
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except json.JSONDecodeError as e: # Erro permanente
        logger.error("Falha de decodificação do JSON. Enviando para DLQ.", extra={'error': str(e)})
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    # except pymongo.errors.AutoReconnect as e: # Exemplo de erro transitório
    #     logger.warning("Erro de conexão com o Mongo. Rejeitando para retentativa.", extra={'error': str(e)})
    #     # Aqui entraria a lógica de publicar em uma fila de retry
    #     ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True) # Exemplo simples: requeue
    except Exception as e: # Outros erros
        logger.error("Falha inesperada ao processar mensagem. Enviando para DLQ.", extra={'error': str(e)})
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def start_consumer(config: Dict[str, Any]) -> None:
    killer = GracefulKiller()
    mongo_client: MongoClient = None
    connection = None

    while not killer.kill_now:
        try:
            mongo_client, mongo_config = get_mongo_client()
            db = mongo_client[mongo_config["db_name"]]
            collection = db[mongo_config["collection_messages"]]

            credentials = pika.PlainCredentials(config['user'], config['password'])
            parameters = pika.ConnectionParameters(host=config['host'], credentials=credentials, heartbeat=3600)
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()

            dlx_name = 'dlx_exchange'
            error_queue = config['queue_error']
            channel.exchange_declare(exchange=dlx_name, exchange_type='direct')
            channel.queue_declare(queue=error_queue, durable=True)
            channel.queue_bind(exchange=dlx_name, queue=error_queue)

            queue_args = {"x-dead-letter-exchange": dlx_name}
            channel.queue_declare(queue=config['queue'], durable=True, arguments=queue_args)
            
            channel.basic_qos(prefetch_count=10) 
            
            on_message_callback = functools.partial(callback, mongo_collection=collection)
            channel.basic_consume(queue=config['queue'], on_message_callback=on_message_callback)

            logger.info("Consumidor iniciado. Aguardando mensagens...")
            while not killer.kill_now and channel.is_open:
                connection.process_data_events(time_limit=1)

        except (pika.exceptions.AMQPConnectionError, pika.exceptions.StreamLostError) as e:
            logger.error("Conexão com RabbitMQ perdida. Tentando reconectar em 5 segundos...", extra={'error': str(e)})
            if connection and not connection.is_closed:
                connection.close()
            time.sleep(5)
        except Exception as e:
            logger.critical("Erro crítico irrecuperável no consumidor.", extra={'error': str(e)})
            break
        finally:
            if connection and not connection.is_closed:
                connection.close()
            if mongo_client:
                mongo_client.close()
            logger.info("Conexões fechadas.")

    logger.info("Consumidor encerrado.")