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
        handler = logging.StreamHandler(sys.stdout)
        
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s'
        )
        
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Impede que o log seja propagado para o logger raiz, evitando duplicação.
        logger.propagate = False
        
    return logger