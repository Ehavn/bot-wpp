# services/worker_ai.py
import json
from src.utils.rabbit_client import get_rabbit_connection, setup_queues
from src.utils.logger import get_logger

class WorkerAI:
    def __init__(self, gemini, whatsapp, pdf_manager):
        """
        gemini: instância do GeminiConnector
        whatsapp: instância do WhatsAppChat
        pdf_manager: instância do PDFManager para obter contexto
        """
        self.gemini = gemini
        self.whatsapp = whatsapp
        self.pdf_manager = pdf_manager
        self.logger = get_logger("WorkerAI")

        # Configura a conexão com RabbitMQ
        self.rabbit_connection, self.rabbit_config = get_rabbit_connection()
        self.channel = self.rabbit_connection.channel()
        setup_queues(self.channel, self.rabbit_config)

    def _callback(self, ch, method, properties, body):
        try:
            package = json.loads(body)
            current_message = package.get("current_message", {})
            history = package.get("history", [])
            
            phone_number = current_message.get("phone_number")
            content = current_message.get("content")
            
            if not all([phone_number, content]):
                self.logger.warning("Mensagem recebida sem phone_number ou content. Descartando.")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            self.logger.info(f"Processando pacote para {phone_number}")

            # 1. Pega contexto de um PDF (exemplo: 'documento_geral.pdf')
            # Você pode criar uma lógica para escolher o PDF certo aqui
            contexto_pdf = self.pdf_manager.get_resumo("documento_geral.pdf")

            # 2. Envia para o Gemini com o contexto do PDF
            bot_resposta = self.gemini.enviar_mensagem(content, contexto=contexto_pdf)
            self.logger.info(f"[Gemini] Resposta gerada: {bot_resposta[:80]}...")

            # 3. Envia resposta para o usuário via WhatsApp
            self.whatsapp.send_whatsapp_message(phone_number, bot_resposta)
            
            # 4. Confirma que a mensagem foi processada com sucesso
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            self.logger.error(f"Erro ao processar pacote da fila: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def run(self):
        """Inicia o consumo da fila de mensagens prontas para a IA."""
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.rabbit_config["queue_ia_messages"],
            on_message_callback=self._callback
        )
        self.logger.info("Worker da IA iniciado. Aguardando mensagens na fila...")
        self.channel.start_consuming()