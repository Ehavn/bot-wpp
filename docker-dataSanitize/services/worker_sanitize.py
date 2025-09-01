from dao.message_dao import MessageDAO
from services.sanitizer import Sanitizer
from utils.mongo_client import get_mongo_client
from utils.logger import get_logger

class WorkerSanitize:
    def __init__(self):
        client, config = get_mongo_client()
        self.dao = MessageDAO(client, config)
        self.sanitizer = Sanitizer()
        self.logger = get_logger("WorkerSanitize")

    def run(self):
        messages = self.dao.get_pending_messages()
        self.logger.info(f"Encontradas {len(messages)} mensagens pendentes.")

        for msg in messages:
            sanitized_text = self.sanitizer.sanitize(msg.get("content", ""))
            self.dao.update_message_status(msg["_id"], "sanitized", new_content=sanitized_text)
            self.logger.info(f"Mensagem {msg['_id']} sanitizada.")
