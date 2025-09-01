import logging

# Configuração básica para logs customizados
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("utils")

def validate_payload(payload: dict) -> bool:
    """Valida se o payload recebido do WhatsApp tem os campos esperados"""
    if not payload:
        return False
    if "value" not in payload:
        return False
    if "messages" not in payload["value"]:
        return False
    return True
