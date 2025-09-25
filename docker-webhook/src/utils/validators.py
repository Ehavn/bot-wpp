import logging

logger = logging.getLogger(__name__)

def validate_whatsapp_payload(payload: dict) -> bool:
    """
    Valida a estrutura de um payload do WhatsApp, navegando corretamente
    até a lista de mensagens.
    """
    try:
        # Caminho correto para encontrar a lista de mensagens dentro do payload
        messages = payload['entry'][0]['changes'][0]['value']['messages']
    except (KeyError, IndexError):

        # contêm a chave 'messages'. O log informa isso e a função retorna False.
        logger.info("Payload recebido não é uma mensagem de usuário (ex: notificação de status). Ignorando.")
        return False
    
    # Verifica se 'messages' é uma lista e não está vazia
    if not isinstance(messages, list) or not messages:
        logger.warning("Validação falhou: 'messages' foi encontrado mas está vazio ou não é uma lista.")
        return False

    # Verifica se cada item na lista é um dicionário com chaves essenciais
    for msg in messages:
        if not isinstance(msg, dict) or 'id' not in msg or 'from' not in msg:
            logger.warning(
                "Validação falhou: item na lista 'messages' não é um dicionário ou não contém 'id'/'from'.",
                extra={'message_snippet': str(msg)[:100]}
            )
            return False

    # Se todas as verificações passaram
    return True