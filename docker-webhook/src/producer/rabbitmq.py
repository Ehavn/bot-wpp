import pika
import json
import os
import logging
import time # Importado para usar no sleep
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
        Estabelece a conexão com o RabbitMQ com uma lógica de retentativa
        e backoff exponencial.
        """
        max_retries = 5
        retry_delay = 1  # segundos

        for attempt in range(max_retries):
            try:
                credentials = pika.PlainCredentials(self.user, self.password)
                parameters = pika.ConnectionParameters(host=self.host, credentials=credentials)
                self._connection = pika.BlockingConnection(parameters)
                self._channel = self._connection.channel()
                self._channel.queue_declare(queue=self.queue_name, durable=True)
                logger.info(
                    "conexao com rabbitmq estabelecida",
                    extra={'host': self.host, 'queue': self.queue_name}
                )
                return # Se a conexão for bem-sucedida, sai da função
            except pika.exceptions.AMQPConnectionError as e:
                logger.warning(
                    "falha ao conectar com o rabbitmq",
                    extra={
                        'error_message': str(e),
                        'attempt': f"{attempt + 1}/{max_retries}",
                        'next_try_in_seconds': retry_delay
                    }
                )
                if attempt + 1 < max_retries:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Dobra o tempo de espera para a próxima tentativa
                else:
                    logger.error("nao foi possivel conectar ao rabbitmq apos varias tentativas")
                    raise # Levanta a exceção se todas as tentativas falharem

    def publish(self, msg: dict):
        """Publica uma mensagem com lógica de reconexão e retentativa."""
        try:
            if not self._connection or self._connection.is_closed:
                logger.warning(
                    "conexao com rabbitmq perdida ou fechada, tentando reconectar",
                    extra={'reason': 'reconnecting'}
                )
                self.connect() # A nova função connect já tem as retentativas

            self._channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=json.dumps(msg),
                properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
            )
        except (pika.exceptions.StreamLostError, pika.exceptions.ChannelClosed) as e:
            logger.error(
                "conexao perdida ao tentar publicar",
                extra={'error_message': str(e), 'error_type': type(e).__name__, 'reason': 'reconnecting_and_retrying'}
            )
            self.connect()
            logger.info("reconexao bem-sucedida, reenviando mensagem")
            self._channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=json.dumps(msg),
                properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
            )
        except Exception as e:
            logger.error(
                "erro inesperado ao publicar no rabbitmq",
                extra={'error_message': str(e), 'error_type': type(e).__name__}
            )
            raise

    def close(self):
        """Fecha a conexão com o RabbitMQ."""
        if self._connection and self._connection.is_open:
            self._connection.close()
            logger.info(
                "conexao com rabbitmq fechada",
                extra={'host': self.host}
            )