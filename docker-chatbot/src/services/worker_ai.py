# services/worker_ai.py
import json
from src.utils.rabbit_client import get_rabbit_connection, setup_queues
from src.utils.logger import get_logger

class WorkerAI:
    def __init__(self, gemini, whatsapp, pdf_manager):
        self.gemini = gemini
        self.whatsapp = whatsapp
        self.pdf_manager = pdf_manager
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

            contexto_final_para_ia = ""
            contextos_individuais = []
            
            if self.pdf_manager.documentos:
                self.logger.info(f"Combinando contexto de {len(self.pdf_manager.documentos)} PDFs...")
                for nome_do_pdf in self.pdf_manager.documentos.keys():
                    
                    # --- MUDANÇA PRINCIPAL AQUI ---
                    # Trocamos get_resumo() por get_texto() para pegar o conteúdo completo.
                    texto_do_pdf = self.pdf_manager.get_texto(nome_do_pdf)
                    
                    contextos_individuais.append(f"--- Início do Documento: {nome_do_pdf} ---\n{texto_do_pdf}\n--- Fim do Documento: {nome_do_pdf} ---")
                
                contexto_final_para_ia = "\n\n".join(contextos_individuais)
            else:
                self.logger.warning("Nenhum PDF carregado. A IA responderá sem contexto adicional.")

            bot_resposta = self.gemini.enviar_mensagem(content, contexto=contexto_final_para_ia)
            self.logger.info(f"[Gemini] Resposta gerada: {bot_resposta[:80]}...")

            self.whatsapp.send_whatsapp_message(phone_number, bot_resposta)
            
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            self.logger.error(f"Erro ao processar pacote da fila: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def run(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.rabbit_config["queue"],
            on_message_callback=self._callback
        )
        self.logger.info(f"Worker da IA iniciado. Aguardando mensagens na fila '{self.rabbit_config['queue']}'...")
        self.channel.start_consuming()