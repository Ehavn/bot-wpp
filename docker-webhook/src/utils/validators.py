import logging

logger = logging.getLogger(__name__)

def validate_whatsapp_payload(payload: dict) -> bool:
    """
    Valida a estrutura de um payload de mensagem do WhatsApp.
    Esta versão espera uma estrutura mais direta, sem os campos 'entry' e 'changes'.
    """
    try:
        # Verifica se 'value' é um dicionário e se 'messages' é uma lista não vazia dentro dele
        if (
            isinstance(payload.get("value"), dict) and
            isinstance(payload["value"].get("messages"), list) and
            payload["value"]["messages"]
        ):
            return True
    except (KeyError, TypeError):
        # Pega qualquer erro que possa ocorrer ao navegar pela estrutura
        logger.warning("Validação falhou devido a uma estrutura de payload inesperada.")
        return False

    logger.warning("Validação falhou. A estrutura do payload não corresponde ao esperado.")
    return False