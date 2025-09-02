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
        # setup_queues(self.channel, self.rabbit_config) # Removido para evitar re-declaração desnecessária

    def _callback(self, ch, method, properties, body):
        try:
            package = json.loads(body)
            current_message = package.get("current_message", {})
            # A variável history não é usada nesta lógica, mas pode ser no futuro
            # history = package.get("history", [])
            
            # --- MUDANÇA 1: Lendo as chaves corretas do JSON ---
            phone_number = current_message.get("from")
            text_object = current_message.get("text", {})
            content = text_object.get("body") if isinstance(text_object, dict) else text_object
            
            if not all([phone_number, content]):
                self.logger.warning(f"Mensagem recebida sem 'from' ou 'text.body'. Descartando: {current_message}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            self.logger.info(f"Processando pacote para {phone_number} com a mensagem: '{content}'")

            # --- MUDANÇA 2: Usando o contexto dos PDFs de forma dinâmica ---
            contexto_pdf = ""
            # Verifica se algum documento PDF foi carregado pelo PDFManager
            if self.pdf_manager.documents:
                # Pega o nome do primeiro PDF encontrado para usar como contexto
                primeiro_pdf = list(self.pdf_manager.documents.keys())[0]
                contexto_pdf = self.pdf_manager.get_resumo(primeiro_pdf)
                self.logger.info(f"Usando contexto do PDF: '{primeiro_pdf}'")
            else:
                self.logger.warning("Nenhum PDF carregado. A IA responderá sem contexto adicional.")

            # 2. Envia para o Gemini com o contexto do PDF
            bot_resposta = self.gemini.enviar_mensagem(content, contexto=contexto_pdf)
            self.logger.info(f"[Gemini] Resposta gerada: {bot_resposta[:80]}...")

            # 3. Envia resposta para o usuário via WhatsApp
            self.whatsapp.send_whatsapp_message(phone_number, bot_resposta)
            
            # 4. Confirma que a mensagem foi processada com sucesso
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            self.logger.error(f"Erro ao processar pacote da fila: {e}")
            # Rejeita a mensagem e não a coloca de volta na fila
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def run(self):
        """Inicia o consumo da fila de mensagens prontas para a IA."""
        self.channel.basic_qos(prefetch_count=1) # Processa uma mensagem por vez
        self.channel.basic_consume(
            queue=self.rabbit_config["queue"], # Usa a fila definida no config
            on_message_callback=self._callback
        )
        self.logger.info(f"Worker da IA iniciado. Aguardando mensagens na fila '{self.rabbit_config['queue']}'...")
        self.channel.start_consuming()