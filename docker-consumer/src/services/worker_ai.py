# Arquivo: src/services/worker_ai.py (Padronizado)
import pika
import time
import json
from src.utils.logger import get_logger
from src.config import config
from src.utils.rabbit_client import setup_queues

class WorkerAI:
    def __init__(self):
        self.logger = get_logger("WorkerAI_Service")
        # CORREÇÃO AQUI
        self.rabbit_host = config.RABBITMQ_HOST
        self.rabbit_user = config.RABBITMQ_USER
        self.rabbit_password = config.RABBITMQ_PASSWORD
        self.queue_name = config.RABBITMQ_QUEUE_IA
        self.connection = None
        self.channel = None
        self.logger.info("Worker AI instanciado.")

    def _connect(self):
        credentials = pika.PlainCredentials(self.rabbit_user, self.rabbit_password)
        while True:
            try:
                self.logger.info(f"Tentando conectar ao RabbitMQ em {self.rabbit_host}...")
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=self.rabbit_host, credentials=credentials)
                )
                self.channel = self.connection.channel()
                self.logger.info("Conexão com RabbitMQ estabelecida com sucesso!")
                
                # Usa os atributos padronizados para o setup
                rabbit_config_dict = {
                    "queue_new_messages": config.RABBITMQ_QUEUE_NEW,
                    "queue_ia_messages": config.RABBITMQ_QUEUE_IA
                }
                setup_queues(self.channel, rabbit_config_dict)
                
                break
            except pika.exceptions.AMQPConnectionError as e:
                self.logger.error(f"Não foi possível conectar ao RabbitMQ: {e}. Tentando novamente em 5 segundos...")
                time.sleep(5)

    def _callback(self, ch, method, properties, body):
        self.logger.info(f" [x] Pacote recebido da fila '{self.queue_name}': {body.decode()}")
        try:
            package = json.loads(body)
            self.logger.info(" [x] Pacote processado pela IA.")
        except Exception as e:
            self.logger.error(f"Erro inesperado ao processar o pacote da IA: {e}", exc_info=True)
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def run(self):
        self._connect()
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self._callback)
        self.logger.info(f" [*] Worker pronto. Esperando por pacotes na fila '{self.queue_name}'. Para sair, pressione CTRL+C")
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.logger.info("Consumo interrompido.")
            self.connection.close()