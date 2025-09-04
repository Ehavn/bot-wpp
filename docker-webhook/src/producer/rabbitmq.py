import pika
import json
import os
import logging
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
        """Estabelece a conexão e o canal com o RabbitMQ."""
        try:
            credentials = pika.PlainCredentials(self.user, self.password)
            parameters = pika.ConnectionParameters(host=self.host, credentials=credentials)
            self._connection = pika.BlockingConnection(parameters)
            self._channel = self._connection.channel()
            self._channel.queue_declare(queue=self.queue_name, durable=True)
            logger.info("Conexão com RabbitMQ estabelecida com sucesso.")
        except Exception as e:
            logger.error(f"Falha ao conectar com o RabbitMQ: {e}")
            raise

    def publish(self, msg: dict):
        """Publica uma mensagem, reutilizando a conexão existente."""
        try:
            if not self._connection or self._connection.is_closed:
                logger.warning("Conexão com RabbitMQ perdida. Tentando reconectar...")
                self.connect()

            self._channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=json.dumps(msg),
                properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
            )
        except Exception as e:
            logger.error(f"Erro ao publicar mensagem no RabbitMQ: {e}")
            # Em caso de falha, é uma boa prática tentar reconectar na próxima vez
            self._connection = None 
            raise

    def close(self):
        """Fecha a conexão com o RabbitMQ."""
        if self._connection and self._connection.is_open:
            self._connection.close()
            logger.info("Conexão com RabbitMQ fechada.")