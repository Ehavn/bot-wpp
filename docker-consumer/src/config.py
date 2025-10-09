# Arquivo: src/config.py (Padronizado)
import os
import json
import logging

class AppConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
            cls._instance._init_config()
        return cls._instance

    def _init_config(self):
        self.logger = logging.getLogger("AppConfig")
        self._load_from_json()
        self._load_from_env()
        self._validate()
        self.logger.info("Configuração carregada com sucesso.")

    def _load_from_json(self):
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.json')
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Arquivo '{config_path}' não encontrado.")
            config_data = {}

        mongo_cfg = config_data.get("mongo", {})
        self.MONGO_URI = mongo_cfg.get("connectionUri")
        self.MONGO_DB_NAME = mongo_cfg.get("db_name", "messages")
        self.MONGO_COLLECTION_RAW = mongo_cfg.get("collection_raw", "raw")

        # CORREÇÃO AQUI
        rabbit_cfg = config_data.get("rabbitmq", {})
        self.RABBITMQ_HOST = rabbit_cfg.get("host", "localhost")
        self.RABBITMQ_USER = rabbit_cfg.get("user")
        self.RABBITMQ_PASSWORD = rabbit_cfg.get("password")
        self.RABBITMQ_QUEUE_NEW = rabbit_cfg.get("queue_new_messages", "new_messages")
        self.RABBITMQ_QUEUE_IA = rabbit_cfg.get("queue_ia_messages", "ia_messages")

    def _load_from_env(self):
        self.MONGO_URI = os.getenv("MONGO_CONNECTION_URI", self.MONGO_URI)
        # CORREÇÃO AQUI
        self.RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", self.RABBITMQ_HOST)
        self.RABBITMQ_USER = os.getenv("RABBITMQ_USER", self.RABBITMQ_USER)
        self.RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", self.RABBITMQ_PASSWORD)

    def _validate(self):
        required_vars = {
            "MONGO_URI": self.MONGO_URI,
            # CORREÇÃO AQUI
            "RABBITMQ_USER": self.RABBITMQ_USER,
            "RABBITMQ_PASSWORD": self.RABBITMQ_PASSWORD,
        }
        missing_vars = [key for key, value in required_vars.items() if not value]
        if missing_vars:
            raise ValueError(f"Configurações essenciais ausentes: {', '.join(missing_vars)}.")

config = AppConfig()