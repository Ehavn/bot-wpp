import os
import json
import pika
from datetime import datetime
from zoneinfo import ZoneInfo

from src.utils.rabbit_client import get_rabbit_connection, setup_queues_and_exchanges
from src.utils.logger import get_logger

def get_greeting():
    """Retorna a saudação correta ('Bom dia', 'Boa tarde' ou 'Boa noite') 
    baseada no horário de São Paulo."""
    now = datetime.now(ZoneInfo("America/Sao_Paulo"))
    hour = now.hour
    
    if 5 <= hour < 12:
        return "Bom dia"
    elif 12 <= hour < 18:
        return "Boa tarde"
    else:
        return "Boa noite"

class WorkerAI:
    def __init__(self, gemini, whatsapp, pdf_manager, message_dao):
        self.gemini = gemini
        self.whatsapp = whatsapp
        self.pdf_manager = pdf_manager
        self.message_dao = message_dao
        self.logger = get_logger("WorkerAI")
        
        self.ai_name = os.getenv("AI_NAME", "Assistente")
        self.system_prompt = os.getenv("AI_SYSTEM_PROMPT", "Você é um assistente virtual.")
        self.logger.info(f"Personalidade da IA carregada. Nome: {self.ai_name}")
        
        try:
            self.rabbit_connection, self.rabbit_config = get_rabbit_connection()
            self.channel = self.rabbit_connection.channel()
            setup_queues_and_exchanges(self.channel, self.rabbit_config)
        except Exception as e:
            self.logger.error(f"Falha ao configurar o RabbitMQ: {e}", exc_info=True)
            raise

    def _formatar_historico_para_ia(self, historico_pacote, contexto_pdf, mensagem_atual, saudacao: str):
        prompt_sistema = self.system_prompt.format(ai_name=self.ai_name, saudacao=saudacao)
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
        trace_id = f"{method.delivery_tag}-{datetime.utcnow().timestamp()}"
        log_context = {"delivery_tag": method.delivery_tag, "trace_id": trace_id}
        
        try:
            package = json.loads(body)
            
            if package.get("action") == "verificar_info_e_responder":
                phone_number = package["phone_number"]
                # REFINADO: Recupera o trace_id original para manter o rastreamento
                original_trace_id = package.get("trace_id", trace_id)
                log_context["trace_id"] = original_trace_id
                
                self.logger.info("Recebido 'lembrete' para verificação.", extra=log_context)
                
                import time
                time.sleep(5) 
                resultado_verificacao = "Obrigado por aguardar! Verifiquei e encontrei as opções de plano X e Y para você."

                self.whatsapp.send_whatsapp_message(phone_number, resultado_verificacao)
                
                ai_message_doc = { "conversationId": phone_number, "from": self.ai_name, "text": {"body": resultado_verificacao}, "role": "ia", "status": "processed", "created_at": datetime.utcnow(), "trace_id": original_trace_id }
                self.message_dao.insert_message(ai_message_doc)
                self.logger.info("Resposta final (pós-verificação) enviada e salva.", extra=log_context)

                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            current_message = package.get("current_message", {})
            phone_number = current_message.get("from", "unknown")
            log_context["conversationId"] = phone_number

            content = current_message.get("text", {}).get("body", "")
            
            if not all([phone_number, content, phone_number != "unknown"]):
                self.logger.warning("Mensagem inválida ou incompleta. Descartando.", extra={"package": package, **log_context})
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            self.logger.info(f"Processando mensagem: '{content}'", extra=log_context)
            
            history_from_package = package.get("history", [])
            contexto_pdf = "\n\n".join(self.pdf_manager.documentos.values())
            saudacao_do_dia = get_greeting()

            historico_formatado = self._formatar_historico_para_ia(history_from_package, contexto_pdf, content, saudacao=saudacao_do_dia)
            bot_resposta = self.gemini.enviar_mensagem(historico_formatado)
            self.logger.info(f"[Gemini] Resposta gerada com sucesso.", extra=log_context)

            if bot_resposta.strip().startswith("[VERIFICAR_INFO]"):
                self.logger.info("Gatilho [VERIFICAR_INFO] detectado. Agendando lembrete.", extra=log_context)
                
                mensagem_de_espera = bot_resposta.replace("[VERIFICAR_INFO]", "").strip()
                self.whatsapp.send_whatsapp_message(phone_number, mensagem_de_espera)
                
                ai_message_doc = { "conversationId": phone_number, "from": self.ai_name, "text": {"body": mensagem_de_espera}, "role": "ia", "status": "processed", "created_at": datetime.utcnow(), "trace_id": trace_id }
                self.message_dao.insert_message(ai_message_doc)
                
                # REFINADO: Adiciona o trace_id ao lembrete para rastreamento
                lembrete = { "action": "verificar_info_e_responder", "phone_number": phone_number, "trace_id": trace_id }
                headers = {'x-delay': 5000}
                self.channel.basic_publish(
                    exchange='delayed_exchange',
                    routing_key=self.rabbit_config["queue"],
                    body=json.dumps(lembrete),
                    properties=pika.BasicProperties(headers=headers, delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
                )

            else:
                self.whatsapp.send_whatsapp_message(phone_number, bot_resposta)
                ai_message_doc = { "conversationId": phone_number, "from": self.ai_name, "text": {"body": bot_resposta}, "role": "ia", "status": "processed", "created_at": datetime.utcnow(), "trace_id": trace_id }
                self.message_dao.insert_message(ai_message_doc)
                self.logger.info("Resposta da IA enviada e salva no MongoDB.", extra=log_context)
            
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            self.logger.error(f"Erro ao processar pacote. Enviando para a DLQ.", exc_info=True, extra={"package": package, **log_context})
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def run(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.rabbit_config["queue"],
            on_message_callback=self._callback
        )
        self.logger.info(f"Aguardando mensagens na fila '{self.rabbit_config['queue']}'...")
        self.channel.start_consuming()