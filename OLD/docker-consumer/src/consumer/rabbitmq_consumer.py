import pika
import json
import functools
import time
import signal
import uuid
from pymongo.errors import ConnectionFailure, OperationFailure
from src.utils.logger import get_logger
from src.utils.mongo_client import get_mongo_client
from src.consumer.processing import MessageProcessor

from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties
from typing import Dict, Any

logger = get_logger(__name__)

# -----------------------------
# Graceful shutdown
# -----------------------------
class GracefulKiller:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        logger.info("Sinal de encerramento recebido. Finalizando o consumidor...")
        self.kill_now = True

# -----------------------------
# Callback da fila
# -----------------------------
def callback(
    ch: BlockingChannel, 
    method: Basic.Deliver, 
    properties: BasicProperties, 
    body: bytes, 
    processor: MessageProcessor,
    retry_config: Dict[str, str]
) -> None:
    
    correlation_id = properties.correlation_id or str(uuid.uuid4())
    extra_fields = {'correlation_id': correlation_id, 'delivery_tag': method.delivery_tag}

    logger.info("Mensagem recebida", extra=extra_fields)
    
    try:
        inserted_id = processor.execute(body)
        logger.info("Mensagem processada e inserida com sucesso", extra={'inserted_id': inserted_id, **extra_fields})
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except (ConnectionFailure, OperationFailure) as e:
        logger.warning(
            "Erro transitório de banco de dados. Enviando para fila de espera para retentativa.",
            extra={'error': str(e), **extra_fields}
        )
        ch.basic_publish(
            exchange=retry_config['retry_exchange'],
            routing_key=retry_config['wait_queue'],
            properties=properties,
            body=body
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except json.JSONDecodeError as e:
        logger.error("Falha de decodificação do JSON. Enviando para DLQ.", extra={'error': str(e), **extra_fields})
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        logger.error("Falha inesperada ao processar mensagem. Enviando para DLQ.", extra={'error': str(e), **extra_fields})
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

# -----------------------------
# Inicializa o consumidor
# -----------------------------
def start_consumer(config: Dict[str, Any]) -> None:
    killer = GracefulKiller()
    
    while not killer.kill_now:
        connection = None
        mongo_client = None
        try:
            # Conecta ao Mongo
            mongo_client, mongo_config = get_mongo_client()
            db = mongo_client[mongo_config["db_name"]]
            collection = db[mongo_config["collection_messages"]]

            # Processador
            processor = MessageProcessor(mongo_collection=collection)

            # Conexão RabbitMQ
            credentials = pika.PlainCredentials(config['user'], config['password'])
            parameters = pika.ConnectionParameters(host=config['host'], credentials=credentials, heartbeat=3600)
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()

            # Dead-letter exchange e fila de erro
            dlx_name = 'dlx_exchange'
            error_queue = config['queue_error']
            channel.exchange_declare(exchange=dlx_name, exchange_type='direct')
            channel.queue_declare(queue=error_queue, durable=True)
            channel.queue_bind(exchange=dlx_name, queue=error_queue)

            # Retry / wait queue
            retry_exchange = ''
            retry_routing_key = config['queue_messages']
            wait_queue = f"{config['queue_messages']}_wait_5s"

            channel.queue_declare(
                queue=wait_queue,
                durable=True,
                arguments={
                    'x-message-ttl': 5000,
                    'x-dead-letter-exchange': retry_exchange,
                    'x-dead-letter-routing-key': retry_routing_key,
                }
            )

            # Fila principal
            queue_args = {"x-dead-letter-exchange": dlx_name}
            channel.queue_declare(queue=config['queue_messages'], durable=True, arguments=queue_args)

            channel.basic_qos(prefetch_count=10) 
            
            retry_config = {"retry_exchange": retry_exchange, "wait_queue": wait_queue}
            
            on_message_callback = functools.partial(
                callback,
                processor=processor,
                retry_config=retry_config
            )
            channel.basic_consume(queue=config['queue_messages'], on_message_callback=on_message_callback)

            logger.info("Consumidor iniciado. Aguardando mensagens...")
            while not killer.kill_now and channel.is_open:
                connection.process_data_events(time_limit=1)

        except (pika.exceptions.AMQPConnectionError, pika.exceptions.StreamLostError) as e:
            logger.error("Conexão com RabbitMQ perdida. Tentando reconectar em 5 segundos...", extra={'error': str(e)})
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
