import json
import pika
import signal
import time
from ..utils.rabbit_client import get_rabbit_connection, setup_queues
from ..utils.mongo_client import get_mongo_client
from ..dao.message_dao import MessageDAO
from ..services.sanitizer import Sanitizer
from ..utils.logger import get_logger
from datetime import datetime
from bson import ObjectId

class WorkerPreparer:
    def __init__(self):
        self.logger = get_logger("WorkerPreparer")
        
        self.shutdown_flag = False
        signal.signal(signal.SIGINT, self.shutdown_handler)
        signal.signal(signal.SIGTERM, self.shutdown_handler)

        self.rabbit_connection, self.rabbit_config = get_rabbit_connection()
        self.channel = self.rabbit_connection.channel()
        setup_queues(self.channel, self.rabbit_config)
        
        self.mongo_client, self.mongo_config = get_mongo_client()
        self.message_dao = MessageDAO(self.mongo_client, self.mongo_config)
        self.sanitizer = Sanitizer()
        self.logger.info("WorkerPreparer iniciado e pronto para consumir mensagens.")

    def shutdown_handler(self, signum, frame):
        self.logger.info("Sinal de desligamento recebido! Finalizando...")
        self.shutdown_flag = True
        if self.channel.is_open:
            self.channel.stop_consuming()

    def _callback(self, ch, method, properties, body):
        try:
            message_data = json.loads(body)
            # CORREÇÃO: Usa a chave correta 'queue_new_messages'
            self.logger.info(f"Dados recebidos da fila '{self.rabbit_config['queue_new_messages']}'.")

            messages_to_process = [message_data] if isinstance(message_data, dict) else message_data

            if not isinstance(messages_to_process, list):
                self.logger.warning(f"Formato de mensagem inesperado: {type(message_data)}. Descartando.")
                return

            for raw_message in messages_to_process:
                try:
                    self.process_single_message(raw_message)
                except Exception as e:
                    self.logger.error(f"Falha ao processar mensagem individual: {raw_message}. Erro: {e}", exc_info=True)
        
        except json.JSONDecodeError:
            self.logger.error("Erro ao decodificar JSON da mensagem do RabbitMQ.", exc_info=True)
        except Exception as e:
            self.logger.error(f"Erro inesperado no callback: {e}", exc_info=True)
        
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def _save_and_enrich_message(self, raw_message: dict) -> dict:
        """Adiciona metadados e salva a mensagem no banco, retornando o documento salvo."""
        raw_message['status'] = 'pending'
        raw_message['role'] = 'user'
        raw_message['timestamp_insert'] = datetime.now().isoformat()
        
        saved_message = self.message_dao.save_raw_message(raw_message)
        self.logger.info(f"Mensagem bruta salva no MongoDB com ID: [{saved_message['_id']}]")
        return saved_message

    def _sanitize_message_text(self, message: dict) -> dict:
        """Sanitiza o texto de uma mensagem."""
        if "text" in message and message["text"]:
            text_field = message["text"]
            if isinstance(text_field, dict) and "body" in text_field:
                sanitized_text = self.sanitizer.sanitize(text_field["body"])
                message["text"]["body"] = sanitized_text
            elif isinstance(text_field, str):
                message["text"] = self.sanitizer.sanitize(text_field)
            self.logger.info(f"Texto da mensagem ID [{message['_id']}] sanitizado.")
        return message

    def _build_and_publish_package(self, message: dict, history: list):
        """Monta o pacote final e publica na fila da IA."""
        package_for_ai = {
            "current_message": message,
            "history": history
        }
        ia_queue = self.rabbit_config.get("queue_ia_messages")

        if not ia_queue:
            self.logger.error("Nome da fila 'queue_ia_messages' não encontrado na configuração. A mensagem não será publicada.")
            return

        self.channel.basic_publish(
            exchange='',
            routing_key=ia_queue,
            body=json.dumps(package_for_ai, default=str),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        self.logger.info(f"Pacote para {message['conversationId']} encaminhado para a fila: [{ia_queue}]")

    def process_single_message(self, raw_message: dict):
        """Orquestra o processo de preparação de uma única mensagem."""
        
        processed_message = self._save_and_enrich_message(raw_message)
        message_id = processed_message['_id']

        conversation_id = processed_message.get("conversationId") or processed_message.get("from")
        if not conversation_id:
            self.message_dao.mark_message_as_failed(message_id, "conversationId ou from não encontrado.")
            self.logger.warning(f"Mensagem ID [{message_id}] sem 'conversationId' ou 'from'. Marcando como falha.")
            return
        
        processed_message["conversationId"] = conversation_id
        
        history = self.message_dao.get_history(conversation_id, current_id=message_id)
        self.logger.info(f"Histórico de {len(history)} mensagens encontrado para a conversa: {conversation_id}.")
        
        processed_message = self._sanitize_message_text(processed_message)
        
        self._build_and_publish_package(processed_message, history)
        
        self.message_dao.mark_message_as_processed(message_id)
        self.logger.info(f"Mensagem ID [{message_id}] marcada como 'processed'.")

    def run(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.rabbit_config["queue_new_messages"],
            on_message_callback=self._callback
        )
        
        while not self.shutdown_flag:
            try:
                self.channel.start_consuming()
            except pika.exceptions.ConnectionClosedByBroker:
                break
            except pika.exceptions.AMQPConnectionError:
                self.logger.warning("Conexão perdida. Tentando reconectar em 5 segundos...")
                time.sleep(5)
        
        self.logger.info("Fechando conexões...")
        if self.rabbit_connection and self.rabbit_connection.is_open:
            self.rabbit_connection.close()
        if self.mongo_client:
            self.mongo_client.close()
        self.logger.info("Aplicação encerrada.")