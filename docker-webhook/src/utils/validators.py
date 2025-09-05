import logging

logger = logging.getLogger(__name__)

def validate_whatsapp_payload(payload: dict) -> bool:
    """
    Valida a estrutura real e aninhada de um payload da API do WhatsApp Business.
    """
    try:
        # Verifica a estrutura aninhada passo a passo para garantir que o caminho existe
        if (
            isinstance(payload.get("entry"), list) and
            payload["entry"] and
            isinstance(payload["entry"][0].get("changes"), list) and
            payload["entry"][0]["changes"] and
            isinstance(payload["entry"][0]["changes"][0].get("value"), dict) and
            isinstance(payload["entry"][0]["changes"][0]["value"].get("messages"), list) and
            payload["entry"][0]["changes"][0]["value"]["messages"]
        ):
            # Se a estrutura principal estiver correta, retorna True
            return True
    except (KeyError, IndexError, TypeError):
        # Pega qualquer erro que possa ocorrer ao navegar pela estrutura
        logger.warning("Validação falhou devido a uma estrutura de payload inesperada.")
        return False
    
    logger.warning("Validação falhou. A estrutura do payload não corresponde ao esperado pela API do WhatsApp.")
    return False