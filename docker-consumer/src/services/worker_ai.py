# Arquivo: src/services/worker_ai.py (Versão Definitiva e Corrigida)

import pika
import time
import json
from src.utils.logger import get_logger
from src.config import config
# Importa a mesma função de setup usada pelo outro worker
from src.utils.rabbit_client import setup_queues

class WorkerAI:
    def __init__(self):
        self.logger = get_logger("WorkerAI_Service")
        self.rabbit_host = config.RABBIT_HOST
        self.rabbit_user = config.RABBIT_USER
        self.rabbit_password = config.RABBIT_PASS
        # O nome da fila vem do config central
        self.queue_name = config.RABBIT_QUEUE_IA
        self.connection = None
        self.channel = None
        self.logger.info("Worker AI instanciado.")

    def _connect(self):
        """Tenta se conectar ao RabbitMQ com retries."""
        credentials = pika.PlainCredentials(self.rabbit_user, self.rabbit_password)
        while True:
            try:
                self.logger.info(f"Tentando conectar ao RabbitMQ em {self.rabbit_host}...")
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=self.rabbit_host, credentials=credentials)
                )
                self.channel = self.connection.channel()
                self.logger.info("Conexão com RabbitMQ estabelecida com sucesso!")
                
                # --- A MUDANÇA CRUCIAL ---
                # Usa a função central para garantir que as filas estão configuradas corretamente
                # O 'config' é um objeto, não um dicionário, então passamos um mock de config
                rabbit_config_dict = {
                    "queue_new_messages": config.RABBIT_QUEUE_NEW,
                    "queue_ia_messages": config.RABBIT_QUEUE_IA
                }
                setup_queues(self.channel, rabbit_config_dict)
                
                break
            except pika.exceptions.AMQPConnectionError as e:
                self.logger.error(f"Não foi possível conectar ao RabbitMQ: {e}. Tentando novamente em 5 segundos...")
                time.sleep(5)

    def _callback(self, ch, method, properties, body):
        """Esta função é chamada sempre que uma mensagem é recebida."""
        self.logger.info(f" [x] Pacote recebido da fila '{self.queue_name}': {body.decode()}")
        try:
            package = json.loads(body)
            self.logger.info(" [x] Pacote processado pela IA.")
        except Exception as e:
            self.logger.error(f"Erro inesperado ao processar o pacote da IA: {e}", exc_info=True)
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def run(self):
        """Este método se conecta e inicia o consumo da fila da IA."""
        self._connect()
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self._callback)
        self.logger.info(f" [*] Worker pronto. Esperando por pacotes na fila '{self.queue_name}'. Para sair, pressione CTRL+C")
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.logger.info("Consumo interrompido.")
            self.connection.close()