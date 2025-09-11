import pika
import json
import os
import logging
import time
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

logger = logging.getLogger(__name__)

class RabbitMQProducer:
    def __init__(self):
        self.host = os.getenv("RABBIT_HOST")
        self.user = os.getenv("RABBIT_USER")
        self.password = os.getenv("RABBIT_PASS")
        self.queue_name = os.getenv("QUEUE_NAME")

        if not all([self.host, self.user, self.password, self.queue_name]):
            raise ValueError("Credenciais do RabbitMQ não encontradas nas variáveis de ambiente.")

        self._connection = None
        self._channel = None
        self.connect()

    def connect(self):
        """
        Estabelece a conexão com o RabbitMQ com uma lógica de retentativa.
        """
        max_retries = 5
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                credentials = pika.PlainCredentials(self.user, self.password)
                parameters = pika.ConnectionParameters(
                    host=self.host, 
                    credentials=credentials,
                    heartbeat=600,  # Aumenta o heartbeat para evitar timeouts
                    blocked_connection_timeout=300
                )
                self._connection = pika.BlockingConnection(parameters)
                self._channel = self._connection.channel()
                dlx_args = {'x-dead-letter-exchange': 'dlx_exchange'}
                self._channel.queue_declare(queue='new_messages', durable=True, arguments=dlx_args)
                logger.info(
                    "Conexão com RabbitMQ estabelecida.",
                    extra={'host': self.host, 'queue': self.queue_name}
                )
                return
            except pika.exceptions.AMQPConnectionError as e:
                logger.warning(
                    "Falha ao conectar com o RabbitMQ.",
                    extra={
                        'error_message': str(e),
                        'attempt': f"{attempt + 1}/{max_retries}",
                    }
                )
                if attempt + 1 < max_retries:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logger.error("Não foi possível conectar ao RabbitMQ após várias tentativas.")
                    raise

    def publish(self, msg: dict, max_retries=3):
        """
        Publica uma mensagem com lógica de reconexão e retentativa.
        """
        for attempt in range(max_retries):
            try:
                # Verifica a conexão antes de tentar publicar
                if not self._connection or self._connection.is_closed or not self._channel or self._channel.is_closed:
                    logger.warning("Conexão com RabbitMQ perdida ou fechada, tentando reconectar...")
                    self.connect()

                self._channel.basic_publish(
                    exchange='',
                    routing_key=self.queue_name,
                    body=json.dumps(msg),
                    properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
                )
                
                logger.info("Mensagem publicada com sucesso na fila.", extra={'wamid': msg[0].get('id') if isinstance(msg, list) and msg else 'N/A'})
                return  # Sucesso, sai da função
                
            except (pika.exceptions.StreamLostError, pika.exceptions.ConnectionClosed) as e:
                logger.error(
                    "Conexão perdida ao tentar publicar. Tentando novamente...",
                    extra={'error_message': str(e), 'attempt': f"{attempt + 1}/{max_retries}"}
                )
            
            except Exception as e:
                logger.error(
                    "Erro inesperado ao publicar no RabbitMQ. Tentando novamente...",
                    extra={'error_message': str(e), 'error_type': type(e).__name__}
                )
            
            time.sleep(1) # Espera um pouco antes de tentar novamente

        logger.critical(
            "Não foi possível publicar a mensagem após várias tentativas.",
            extra={'message_snippet': str(msg)[:100]}
        )
        raise Exception("Falha ao publicar mensagem no RabbitMQ")

    def close(self):
        """Fecha a conexão com o RabbitMQ."""
        if self._connection and self._connection.is_open:
            self._connection.close()
            logger.info("Conexão com RabbitMQ fechada.", extra={'host': self.host})