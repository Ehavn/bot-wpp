# src/utils/logger.py
import logging
import sys
import os
from pythonjsonlogger import jsonlogger

def get_logger(name="app"):
    """
    Configura e retorna um logger que formata os logs em JSON.
    """
    logger = logging.getLogger(name)
    
    # Previne a adição de múltiplos handlers se a função for chamada várias vezes
    if not logger.handlers:
        log_handler = logging.StreamHandler(sys.stdout)
        
        # Formato que inclui informações úteis para depuração em produção
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(funcName)s %(lineno)d %(message)s'
        )
        log_handler.setFormatter(formatter)
        
        logger.addHandler(log_handler)
        
        # O nível do log pode ser controlado por uma variável de ambiente
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        logger.setLevel(log_level)
        logger.propagate = False # Evita que o log root duplique as mensagens
        
    return logger