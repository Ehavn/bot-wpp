import logging
from python_json_logger import jsonlogger

def get_logger(name="app"):
    """Configura e retorna um logger que formata mensagens em JSON."""
    logger = logging.getLogger(name)
    
    # Evita adicionar handlers duplicados se a função for chamada múltiplas vezes
    if not logger.handlers:
        handler = logging.StreamHandler()
        
        # Define o formato do log em JSON
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Impede que o log seja propagado para o logger raiz
        logger.propagate = False
        
    return logger