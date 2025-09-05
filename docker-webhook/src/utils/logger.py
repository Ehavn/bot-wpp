import logging
from pythonjsonlogger import jsonlogger
import sys

def get_logger(name: str):
    """
    Configura e retorna um logger que gera saídas em formato JSON.
    """
    logger = logging.getLogger(name)
    
    # Previne a duplicação de handlers se a função for chamada múltiplas vezes
    if not logger.handlers:
        # Envia os logs para a saída padrão (terminal), que é a melhor prática
        # para ambientes como Docker e Google Cloud.
        handler = logging.StreamHandler(sys.stdout)
        
        # Define o formato do log, incluindo campos padrão e permitindo campos extras.
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s'
        )
        
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        # Impede que o log seja propagado para o logger raiz, evitando duplicação.
        logger.propagate = False
        
    return logger