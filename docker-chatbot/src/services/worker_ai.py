# Arquivo: src/services/worker_ai.py

import json
from datetime import datetime
from src.utils.rabbit_client import get_rabbit_connection, setup_queues
from src.utils.logger import get_logger

class WorkerAI:
    def __init__(self, gemini, whatsapp, pdf_manager, message_dao):
        self.gemini = gemini
        self.whatsapp = whatsapp
        self.pdf_manager = pdf_manager
        self.message_dao = message_dao
        self.logger = get_logger("WorkerAI")
        self.rabbit_connection, self.rabbit_config = get_rabbit_connection()
        self.channel = self.rabbit_connection.channel()
        setup_queues(self.channel, self.rabbit_config)

    def _formatar_historico_para_ia(self, historico_pacote, contexto_pdf, mensagem_atual):
        """
        Cria o prompt completo e final para o Gemini.
        """
        # --- PROMPT DE SISTEMA FINAL E DIRETIVO ---
        prompt_sistema = """
        Sua tarefa é atuar como um assistente de atendimento. Você receberá um histórico de chat e uma nova mensagem do usuário. Sua única função é responder à nova mensagem do usuário usando o histórico como contexto.

        REGRAS CRÍTICAS E OBRIGATÓRIAS:
        1. O histórico fornecido é a única fonte de verdade. Responda a perguntas sobre a conversa passada baseando-se EXCLUSIVAMENTE no texto do histórico.
        2. É PROIBIDO e uma falha na sua função se você disser que "não tem memória", "não tem acesso a conversas anteriores" ou dar respostas evasivas sobre privacidade. A conversa está sendo fornecida a você para ser usada.
        3. Responda apenas à última mensagem do usuário.
        """
        
        if contexto_pdf:
            prompt_sistema += f"\n\n--- CONTEXTO ADICIONAL DE DOCUMENTOS ---\n{contexto_pdf}\n--- FIM DO CONTEXTO ---"

        mensagens_para_ia = []
        mensagens_para_ia.append({"role": "system", "parts": [{"text": prompt_sistema}]})

        for msg in historico_pacote:
            role = "user" if msg.get("role") == "user" else "model"
            text_content = msg.get("text", {}).get("body", "") if isinstance(msg.get("text"), dict) else msg.get("text", "")
            if text_content:
                mensagens_para_ia.append({"role": role, "parts": [{"text": text_content}]})
        
        mensagens_para_ia.append({"role": "user", "parts": [{"text": mensagem_atual}]})
        
        return mensagens_para_ia

    def _callback(self, ch, method, properties, body):
        try:
            package = json.loads(body)
            current_message = package.get("current_message", {})
            history_from_package = package.get("history", [])
            phone_number = current_message.get("from")
            text_object = current_message.get("text", {})
            content = text_object.get("body") if isinstance(text_object, dict) else text_object
            
            if not all([phone_number, content]):
                self.logger.warning(f"Mensagem recebida sem 'from' ou 'text.body'. Descartando: {current_message}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            self.logger.info(f"Processando pacote para {phone_number} com a mensagem: '{content}'")
            self.logger.info(f"Recebidas {len(history_from_package)} mensagens no histórico do pacote.")

            contexto_pdf = ""
            if self.pdf_manager.documentos:
                textos_pdfs = [self.pdf_manager.get_texto(nome) for nome in self.pdf_manager.documentos.keys()]
                contexto_pdf = "\n\n".join(textos_pdfs)

            historico_formatado = self._formatar_historico_para_ia(history_from_package, contexto_pdf, content)

            # Adicionando um log para ver o pacote final enviado para a IA
            self.logger.info(f"Payload final para a IA: {json.dumps(historico_formatado, indent=2, ensure_ascii=False)}")

            bot_resposta = self.gemini.enviar_mensagem(historico_formatado)
            self.logger.info(f"[Gemini] Resposta gerada: {bot_resposta[:80]}...")

            self.whatsapp.send_whatsapp_message(phone_number, bot_resposta)
            
            ai_message_doc = {
                "conversationId": phone_number,
                "from": "chatbot_gemini",
                "text": {"body": bot_resposta},
                "role": "ia",
                "status": "processed",
                "created_at": datetime.utcnow()
            }
            self.message_dao.insert_message(ai_message_doc)
            self.logger.info(f"Resposta da IA para {phone_number} salva no MongoDB.")
            
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            self.logger.error(f"Erro ao processar pacote da fila: {e}", exc_info=True)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def run(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.rabbit_config["queue"],
            on_message_callback=self._callback
        )
        self.logger.info(f"Worker da IA iniciado. Aguardando mensagens na fila '{self.rabbit_config['queue']}'...")
        self.channel.start_consuming()