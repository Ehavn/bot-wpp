import os # Importar os
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

        self.ai_name = os.getenv("AI_NAME", "Assistente")
        default_prompt = "Você é um assistente de atendimento. Responda às perguntas do usuário com base no histórico."
        self.system_prompt = os.getenv("AI_SYSTEM_PROMPT", default_prompt)
        self.logger.info(f"Personalidade da IA carregada. Nome: {self.ai_name}")
        
        try:
            self.rabbit_connection, self.rabbit_config = get_rabbit_connection()
            self.channel = self.rabbit_connection.channel()
            setup_queues(self.channel, self.rabbit_config)
        except Exception as e:
            self.logger.error(f"Falha ao configurar o RabbitMQ: {e}", exc_info=True)
            raise

    def _formatar_historico_para_ia(self, historico_pacote, contexto_pdf, mensagem_atual):
        prompt_sistema = self.system_prompt.format(ai_name=self.ai_name)
        
        if contexto_pdf:
            prompt_sistema += f"\n\n--- CONTEXTO ADICIONAL DE DOCUMENTOS ---\n{contexto_pdf}\n--- FIM DO CONTEXTO ---"

        mensagens_para_ia = [{"role": "system", "parts": [{"text": prompt_sistema}]}]

        for msg in historico_pacote:
            role = "user" if msg.get("role") == "user" else "model"
            text_content = msg.get("text", {}).get("body", "") if isinstance(msg.get("text"), dict) else msg.get("text", "")
            if text_content:
                mensagens_para_ia.append({"role": role, "parts": [{"text": text_content}]})
        
        mensagens_para_ia.append({"role": "user", "parts": [{"text": mensagem_atual}]})
        
        return mensagens_para_ia

    def _callback(self, ch, method, properties, body):
        package = {}
        phone_number = "unknown"
        trace_id = f"{method.delivery_tag}-{datetime.utcnow().timestamp()}"
        log_context = {"delivery_tag": method.delivery_tag, "trace_id": trace_id}

        try:
            package = json.loads(body)
            current_message = package.get("current_message", {})
            phone_number = current_message.get("from", "unknown")
            log_context["conversationId"] = phone_number # Adiciona ID da conversa ao log

            text_object = current_message.get("text", {})
            content = text_object.get("body") if isinstance(text_object, dict) else text_object
            
            if not all([phone_number, content, phone_number != "unknown"]):
                self.logger.warning(
                    f"Mensagem inválida ou incompleta. Descartando.",
                    extra={"package": package, **log_context}
                )
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            self.logger.info(f"Processando mensagem: '{content}'", extra=log_context)
            
            history_from_package = package.get("history", [])
            contexto_pdf = "\n\n".join(self.pdf_manager.documentos.values())
            historico_formatado = self._formatar_historico_para_ia(history_from_package, contexto_pdf, content)

            bot_resposta = self.gemini.enviar_mensagem(historico_formatado)
            self.logger.info(f"[Gemini] Resposta gerada com sucesso.", extra=log_context)

            self.whatsapp.send_whatsapp_message(phone_number, bot_resposta)
            
            ai_message_doc = {
                "conversationId": phone_number,
                "from": self.ai_name, # Usa o nome do AI
                "text": {"body": bot_resposta},
                "role": "ia",
                "status": "processed",
                "created_at": datetime.utcnow(),
                "trace_id": trace_id # Salva o ID de rastreamento
            }
            self.message_dao.insert_message(ai_message_doc)
            self.logger.info(f"Resposta da IA salva no MongoDB.", extra=log_context)
            
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            self.logger.error(
                f"Erro ao processar pacote. Enviando para a Dead-Letter Queue.",
                exc_info=True,
                extra={"package": package, **log_context}
            )
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def run(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.rabbit_config["queue"],
            on_message_callback=self._callback
        )
        self.logger.info(f"Aguardando mensagens na fila '{self.rabbit_config['queue']}'...")
        self.channel.start_consuming()