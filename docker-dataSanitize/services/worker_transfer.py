from dao.message_dao import MessageDAO
from utils.mongo_client import get_mongo_client
from utils.logger import get_logger

class WorkerTransfer:
    def __init__(self):
        client, config = get_mongo_client()
        self.dao = MessageDAO(client, config)
        self.logger = get_logger("WorkerTransfer")

    def run(self):
        sanitized_messages = self.dao.get_sanitized_messages()
        self.logger.info(f"Encontradas {len(sanitized_messages)} mensagens sanitizadas.")

        for msg in sanitized_messages:
            self.dao.insert_sanitized_message(msg)
            self.dao.update_message_status(msg["_id"], "transferred")
            self.logger.info(f"Mensagem {msg['_id']} transferida.")
