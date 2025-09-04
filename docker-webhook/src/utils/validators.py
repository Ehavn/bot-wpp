import logging

# Configura um logger para este módulo para que as mensagens apareçam nos logs da aplicação
logger = logging.getLogger(__name__)

def validate_whatsapp_payload(payload: dict) -> bool:
    """
    Valida de forma robusta a estrutura e os tipos de dados esperados
    em um payload de mensagem de texto do WhatsApp.

    Verifica a presença e o tipo de chaves aninhadas, como
    'value', 'messages', e a estrutura interna de cada mensagem.

    Args:
        payload (dict): O dicionário do payload JSON recebido da requisição.

    Returns:
        bool: True se o payload for válido, False caso contrário.
    """
    try:
        # 1. Validação da estrutura principal (nível superior)
        if not isinstance(payload, dict):
            logger.warning("Validação falhou: Payload recebido não é um dicionário.")
            return False

        value = payload.get("value")
        if not isinstance(value, dict):
            logger.warning("Validação falhou: Chave 'value' ausente ou não é um dicionário.")
            return False

        messages = value.get("messages")
        if not isinstance(messages, list) or not messages:
            logger.warning("Validação falhou: Chave 'messages' ausente, não é uma lista ou está vazia.")
            return False

        # 2. Validação de cada mensagem individualmente na lista
        # Garante que cada item tenha a estrutura mínima de uma mensagem de texto
        for message in messages:
            # Usamos .get() em cascata para evitar erros se chaves intermediárias não existirem
            text_dict = message.get("text", {})
            
            if not (
                isinstance(message, dict) and
                isinstance(text_dict, dict) and
                isinstance(text_dict.get("body"), str)
            ):
                logger.warning(f"Validação falhou: A estrutura da mensagem está inválida. Mensagem: {message}")
                return False

        # 3. Se todas as validações passaram, o payload é válido
        return True

    except Exception:
        # Pega qualquer outro erro inesperado durante o acesso aos dados aninhados
        logger.exception("Erro inesperado durante a validação do payload. O payload pode estar severamente malformado.")
        return False