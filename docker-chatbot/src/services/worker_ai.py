# services/worker_ai.py
import json
from datetime import datetime
from src.utils.rabbit_client import get_rabbit_connection, setup_queues
from src.utils.logger import get_logger

class WorkerAI:
    def __init__(self, gemini, whatsapp, pdf_manager, message_dao): # <-- 1. DAO adicionado
        self.gemini = gemini
        self.whatsapp = whatsapp
        self.pdf_manager = pdf_manager
        self.message_dao = message_dao # <-- 2. DAO armazenado
        self.logger = get_logger("WorkerAI")

        self.rabbit_connection, self.rabbit_config = get_rabbit_connection()
        self.channel = self.rabbit_connection.channel()
        setup_queues(self.channel, self.rabbit_config)

    def _callback(self, ch, method, properties, body):
        try:
            package = json.loads(body)
            current_message = package.get("current_message", {})
            
            phone_number = current_message.get("from")
            text_object = current_message.get("text", {})
            content = text_object.get("body") if isinstance(text_object, dict) else text_object
            
            if not all([phone_number, content]):
                self.logger.warning(f"Mensagem recebida sem 'from' ou 'text.body'. Descartando: {current_message}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            self.logger.info(f"Processando pacote para {phone_number} com a mensagem: '{content}'")

            # --- Lógica de contexto (sem alteração) ---
            contexto_final_para_ia = ""
            if self.pdf_manager.documentos:
                textos_pdfs = [self.pdf_manager.get_texto(nome) for nome in self.pdf_manager.documentos.keys()]
                contexto_final_para_ia = "\n\n".join(textos_pdfs)

            # --- Geração da resposta da IA (sem alteração) ---
            bot_resposta = self.gemini.enviar_mensagem(content, contexto=contexto_final_para_ia)
            self.logger.info(f"[Gemini] Resposta gerada: {bot_resposta[:80]}...")

            # --- Envio da resposta para o WhatsApp (sem alteração) ---
            self.whatsapp.send_whatsapp_message(phone_number, bot_resposta)
            
            # --- 3. SALVAR RESPOSTA DA IA NO MONGO (NOVA LÓGICA) ---
            ai_message_doc = {
                "conversationId": phone_number, # Usando o número do usuário como ID da conversa
                "from": "chatbot_gemini", # Identificador do seu bot
                "text": {
                    "body": bot_resposta
                },
                "role": "ia", # <-- Campo 'role' definido
                "status": "processed",
                "created_at": datetime.utcnow() # <-- Campo 'created_at' definido
            }
            self.message_dao.insert_message(ai_message_doc)
            self.logger.info(f"Resposta da IA para {phone_number} salva no MongoDB.")
            # --- FIM DA NOVA LÓGICA ---
            
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            self.logger.error(f"Erro ao processar pacote da fila: {e}")
            # Considerar não reenfileirar mensagens com erro para evitar loops
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def run(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.rabbit_config["queue"],
            on_message_callback=self._callback
        )
        self.logger.info(f"Worker da IA iniciado. Aguardando mensagens na fila '{self.rabbit_config['queue']}'...")
        self.channel.start_consuming()