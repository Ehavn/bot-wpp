import logging

logger = logging.getLogger(__name__)

def validate_whatsapp_payload(payload: dict) -> bool:
    """
    Valida a estrutura de um payload de mensagem do WhatsApp de forma mais robusta.
    """
    try:
        messages = payload.get("value", {}).get("messages", [])

        if not isinstance(messages, list) or not messages:
            logger.warning("Validação falhou: 'messages' não é uma lista ou está vazia.")
            return False

        for msg in messages:
            if not isinstance(msg, dict) or 'id' not in msg or 'from' not in msg:
                logger.warning(
                    "Validação falhou: item na lista 'messages' não é um dicionário ou não contém 'id'/'from'.",
                    extra={'message_snippet': str(msg)[:100]}
                )
                return False

        return True

    except Exception:
        logger.warning("Validação falhou devido a uma estrutura de payload inesperada.")
        return False