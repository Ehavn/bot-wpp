# Arquivo: src/services/worker_preparer.py

import json
import pika
import time
import signal
from ..utils.rabbit_client import get_rabbit_connection, setup_queues
from ..utils.mongo_client import get_mongo_client
from ..dao.message_dao import MessageDAO
from ..services.sanitizer import Sanitizer

class WorkerPreparer:
    def __init__(self):
        self.shutdown_flag = False
        signal.signal(signal.SIGINT, self.shutdown_handler)
        signal.signal(signal.SIGTERM, self.shutdown_handler)
        self.rabbit_connection, self.rabbit_config = get_rabbit_connection()
        self.channel = self.rabbit_connection.channel()
        setup_queues(self.channel, self.rabbit_config)
        self.mongo_client, self.mongo_config = get_mongo_client()
        self.message_dao = MessageDAO(self.mongo_client, self.mongo_config)
        self.sanitizer = Sanitizer()
        print("Iniciando WorkerPreparer...")

    def shutdown_handler(self, signum, frame):
        print("\nSinal de desligamento recebido! Finalizando o trabalho atual e encerrando...")
        self.shutdown_flag = True

    def process_pending_messages(self):
        """Busca e processa uma única mensagem pendente do MongoDB."""
        if self.shutdown_flag:
            return False

        pending_message = self.message_dao.find_and_update_one_pending_message()
        if not pending_message:
            return False

        print(f"Mensagem encontrada para processar. ID: [{pending_message['_id']}]")
        
        try:
            # Pega o ID da mensagem atual para excluí-la do histórico
            current_id = pending_message.get("_id")
            # Usa 'conversationId' como primário e 'from' como fallback
            conversation_id = pending_message.get("conversationId") or pending_message.get("from")
            
            if conversation_id:
                # Chama o método do DAO passando o ID da conversa e o ID da mensagem atual
                history = self.message_dao.get_history(conversation_id, current_id)
                print(f"Histórico completo de {len(history)} mensagens encontrado para a conversa: {conversation_id}.")

                # Lógica robusta para sanitizar o texto
                if "text" in pending_message and pending_message["text"]:
                    text_field = pending_message["text"]
                    
                    if isinstance(text_field, dict) and "body" in text_field:
                        original_text = text_field["body"]
                        sanitized_text = self.sanitizer.sanitize(original_text)
                        pending_message["text"]["body"] = sanitized_text
                        print("Corpo do texto (body) sanitizado.")
                    
                    elif isinstance(text_field, str):
                        sanitized_text = self.sanitizer.sanitize(text_field)
                        pending_message["text"] = sanitized_text
                        print("Texto da mensagem atual sanitizado.")
                    
                    else:
                        print(f"AVISO: Campo 'text' tem um tipo inesperado ({type(text_field)}) e não foi sanitizado.")
                
                # Garante que a mensagem atual tenha o conversationId para consistência futura
                pending_message["conversationId"] = conversation_id
                
                package_for_ai = {
                    "current_message": pending_message,
                    "history": history
                }

                ia_queue = self.rabbit_config.get("queue_ia_messages")
                self.channel.basic_publish(
                    exchange='',
                    routing_key=ia_queue,
                    body=json.dumps(package_for_ai, default=str),
                    properties=pika.BasicProperties(delivery_mode=2) # Mensagem persistente
                )
                print(f"Pacote de dados para {conversation_id} encaminhado para a fila: [{ia_queue}]")

                self.message_dao.mark_message_as_processed(pending_message['_id'])
                print(f"Mensagem ID [{pending_message['_id']}] marcada como 'processed'.")

            else:
                self.message_dao.mark_message_as_failed(pending_message['_id'])
                print(f"AVISO: Mensagem ID [{pending_message['_id']}] sem 'conversationId' ou 'from'. Marcando como falha.")

        except Exception as e:
            print(f"Erro ao processar mensagem ID [{pending_message.get('_id', 'N/A')}]: {e}")
            if pending_message:
                self.message_dao.mark_message_as_failed(pending_message['_id'])
        
        return True

    def run(self):
        print("Aplicação (Preparador) em execução. Buscando mensagens no MongoDB... Pressione CTRL+C para sair.")
        while not self.shutdown_flag:
            try:
                was_message_processed = self.process_pending_messages()
                if not was_message_processed and not self.shutdown_flag:
                    # print("Nenhuma mensagem pendente encontrada. Aguardando 5 segundos...")
                    time.sleep(5)
            except Exception as e:
                print(f"Ocorreu um erro inesperado no loop principal: {e}")
                time.sleep(10)
        
        print("Fechando conexões...")
        if self.rabbit_connection and self.rabbit_connection.is_open:
            self.rabbit_connection.close()
        if self.mongo_client:
            self.mongo_client.close()
        print("Aplicação encerrada.")