import os
import json
import logging

class AppConfig:
    """
    Classe Singleton para carregar e fornecer acesso centralizado
    às configurações da aplicação.

    A ordem de prioridade é:
    1. Variáveis de Ambiente (mais alta)
    2. Arquivo config.json (mais baixa)
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
            cls._instance._init_config()
        return cls._instance

    def _init_config(self):
        """Inicializa e carrega as configurações."""
        self.logger = logging.getLogger("AppConfig")

        # --- Carrega do arquivo config.json ---
        self._load_from_json()

        # --- Sobrescreve com variáveis de ambiente ---
        self._load_from_env()

        # --- Valida se as configurações essenciais estão presentes ---
        self._validate()

        self.logger.info("Configuração carregada com sucesso.")

    def _load_from_json(self):
        """Carrega as configurações base do arquivo JSON."""
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.json')
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Arquivo de configuração '{config_path}' não encontrado. Usando apenas variáveis de ambiente.")
            config_data = {}

        mongo_cfg = config_data.get("mongo", {})
        self.MONGO_URI = mongo_cfg.get("connectionUri")
        self.MONGO_DB_NAME = mongo_cfg.get("db_name", "messages")
        self.MONGO_COLLECTION_RAW = mongo_cfg.get("collection_raw", "raw")

        rabbit_cfg = config_data.get("RABBIT", {})
        self.RABBIT_HOST = rabbit_cfg.get("host", "localhost")
        self.RABBIT_USER = rabbit_cfg.get("user")
        self.RABBIT_PASS = rabbit_cfg.get("password")
        self.RABBIT_QUEUE_NEW = rabbit_cfg.get("queue_new_messages", "new_messages")
        self.RABBIT_QUEUE_IA = rabbit_cfg.get("queue_ia_messages", "ia_messages")

    def _load_from_env(self):
        """Sobrescreve as configurações com valores de variáveis de ambiente, se existirem."""
        self.MONGO_URI = os.getenv("MONGO_CONNECTION_URI", self.MONGO_URI)
        self.RABBIT_HOST = os.getenv("RABBIT_HOST", self.RABBIT_HOST)
        self.RABBIT_USER = os.getenv("RABBIT_USER", self.RABBIT_USER)
        self.RABBIT_PASS = os.getenv("RABBIT_PASS", self.RABBIT_PASS)

    def _validate(self):
        """Verifica se as configurações críticas foram definidas, caso contrário, lança um erro."""
        required_vars = {
            "MONGO_URI": self.MONGO_URI,
            "RABBIT_USER": self.RABBIT_USER,
            "RABBIT_PASS": self.RABBIT_PASS,
        }
        missing_vars = [key for key, value in required_vars.items() if not value]
        if missing_vars:
            raise ValueError(f"Configurações essenciais ausentes: {', '.join(missing_vars)}. Verifique seu .env ou config.json.")

config = AppConfig()