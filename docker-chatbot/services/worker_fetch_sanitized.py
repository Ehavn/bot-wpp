import time
from dao.message_dao import MessageDAO
from utils.mongo_client import get_mongo_client
from utils.logger import get_logger

class WorkerFetchSanitized:
    def __init__(self, gemini=None, whatsapp=None, poll_interval=5):
        """
        gemini: instância do GeminiConnector
        whatsapp: instância do WhatsAppChat
        poll_interval: intervalo em segundos entre buscas
        """
        client, config = get_mongo_client()
        self.dao = MessageDAO(client, config)
        self.logger = get_logger("WorkerFetchSanitized")

        self.gemini = gemini
        self.whatsapp = whatsapp
        self.poll_interval = poll_interval
        self.running = True

        self.logger.info("Worker iniciado")

    def fetch_messages(self):
        """Busca mensagens sanitizadas no Mongo."""
        return self.dao.get_sanitized_messages()

    def mark_as_read(self, message_id):
        """Atualiza status da mensagem para 'read'."""
        self.dao.update_message_status(message_id, "read")

    def run_loop(self):
        """Loop contínuo que processa mensagens sanitizadas."""
        self.logger.info("WorkerFetchSanitized iniciado em loop contínuo.")
        while self.running:
            try:
                messages = self.fetch_messages()
                for msg in messages:
                    # Mostra telefone + conteúdo do Mongo
                    telefone = msg.get("telefone", "desconhecido")
                    conteudo = msg.get("content", "")
                    print(f"[Mongo] Telefone: {telefone} | Conteúdo: {conteudo}")

                    # Envia para Gemini
                    bot_resposta = self.gemini.enviar_mensagem(conteudo)
                    print(f"[Gemini] Resposta: {bot_resposta}")

                    # Envia pelo WhatsApp
                    resultado = self.whatsapp.send_whatsapp_message(bot_resposta)
                    if resultado.get("success"):
                        self.logger.info(f"Mensagem {msg['_id']} enviada pelo WhatsApp!")
                    else:
                        self.logger.warning(
                            f"Falha ao enviar mensagem {msg['_id']}: {resultado.get('response')}"
                        )

                    # Marca mensagem como lida
                    self.mark_as_read(msg["_id"])

            except Exception as e:
                self.logger.error(f"Erro no WorkerFetchSanitized: {e}")

            time.sleep(self.poll_interval)
