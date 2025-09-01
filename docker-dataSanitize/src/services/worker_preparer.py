# src/services/worker_preparer.py
import json
import pika
from src.services.sanitizer import Sanitizer
from src.utils.rabbit_client import get_rabbit_connection, setup_queues
from src.utils.mongo_client import get_mongo_client
from src.dao.message_dao import MessageDAO
from src.utils.logger import get_logger

class WorkerPreparer:
    def __init__(self):
        # Conexão com RabbitMQ
        self.rabbit_connection, self.rabbit_config = get_rabbit_connection()
        self.channel = self.rabbit_connection.channel()
        setup_queues(self.channel, self.rabbit_config)
        
        # Conexão com MongoDB
        mongo_client, mongo_cfg = get_mongo_client()
        self.dao = MessageDAO(mongo_client, mongo_cfg)
        
        self.sanitizer = Sanitizer()
        self.logger = get_logger("WorkerPreparer")

    def _callback(self, ch, method, properties, body):
        try:
            current_message = json.loads(body)
            phone_number = current_message.get("phone_number")
            self.logger.info(f"Preparando mensagem de {phone_number}")

            # 1. Sanitiza a mensagem atual
            sanitized_content = self.sanitizer.sanitize(current_message.get("content", ""))
            current_message["content"] = sanitized_content

            # 2. Busca o histórico de mensagens
            history = self.dao.get_message_history_by_phone(phone_number)
            self.logger.info(f"Encontradas {len(history)} mensagens no histórico.")

            # 3. Monta o pacote final para a IA
            package_for_ia = {
                "current_message": current_message,
                "history": history
            }

            # 4. Publica o pacote na próxima fila
            self.channel.basic_publish(
                exchange='',
                routing_key=self.rabbit_config["queue_ia_messages"],
                body=json.dumps(package_for_ia),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            self.logger.info(f"Pacote para {phone_number} enviado para a fila da IA.")
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            self.logger.error(f"Falha ao preparar mensagem: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def run(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.rabbit_config["queue_new_messages"],
            on_message_callback=self._callback
        )
        self.logger.info("Aguardando novas mensagens para preparar...")
        self.channel.start_consuming()