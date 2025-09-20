# src/services/wpp.py
import os
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from src.utils.logger import get_logger

logger = get_logger("WhatsAppChat")

class WhatsAppChat:
    def __init__(self, debug=False):
        self.token = os.getenv("WHATSAPP_TOKEN")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

        if not all([self.token, self.phone_number_id]):
            raise ValueError("WHATSAPP_TOKEN ou WHATSAPP_PHONE_NUMBER_ID não encontrados no ambiente.")

        self.base_url = f"https://graph.facebook.com/v22.0/{self.phone_number_id}/messages"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        self.debug = debug
        logger.info("WhatsApp Chat inicializado.")

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True
    )
    def send_whatsapp_message(self, recipient_phone: str, text: str):
        """Envia mensagem de texto com retentativas."""
        text = text[:4096]
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_phone,
            "type": "text",
            "text": {"body": text}
        }
        log_context = {"recipient": recipient_phone}

        if self.debug:
            logger.info(f"Enviando mensagem para {recipient_phone}: {text}", extra=log_context)

        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload, timeout=10)
            response.raise_for_status()  # Lança uma exceção para códigos de status HTTP 4xx/5xx

            response_data = response.json()
            if self.debug:
                logger.info("Mensagem enviada com sucesso.", extra={"response": response_data, **log_context})
            return {"success": True, "response": response_data}

        except requests.RequestException as e:
            logger.error(f"Erro ao enviar mensagem para o WhatsApp: {e}", exc_info=True, extra=log_context)
            raise  # Relança a exceção para o decorator @retry