# src/services/worker_ai.py
import json
from src.utils.rabbit_client import get_rabbit_connection, setup_queues
from src.utils.logger import get_logger

class WorkerAI:
    def __init__(self):
        self.connection, self.config = get_rabbit_connection()
        self.channel = self.connection.channel()
        setup_queues(self.channel, self.config)
        self.logger = get_logger("WorkerAI")

    def _callback(self, ch, method, properties, body):
        package = json.loads(body)
        phone_number = package.get("current_message", {}).get("phone_number")
        self.logger.info(f"Recebido pacote para IA do número {phone_number}")

        #
        # AQUI VAI SUA LÓGICA PARA ENVIAR O PACOTE PARA A IA
        #
        # Exemplo:
        # current_msg = package['current_message']
        # history = package['history']
        # ai_response = ai_service.get_response(current_msg, history)
        # send_whatsapp_response(phone_number, ai_response)
        #
        
        self.logger.info(f"Processo de IA para {phone_number} finalizado.")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def run(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.config["queue_ia_messages"],
            on_message_callback=self._callback
        )
        self.logger.info("Aguardando pacotes para IA...")
        self.channel.start_consuming()