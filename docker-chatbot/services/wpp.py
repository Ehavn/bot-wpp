import json
import requests

class WhatsAppChat:
    def __init__(self, config_file="config/config.json", debug=False):
        with open(config_file, "r") as f:
            config = json.load(f)

        whatsapp_config = config.get("whatsapp", {})
        self.token = whatsapp_config.get("token")
        self.phone_number_id = whatsapp_config.get("phone_number_id")
        self.to_number = whatsapp_config.get("to_phone_number")

        if not all([self.token, self.phone_number_id, self.to_number]):
            raise ValueError("Alguma configuração do WhatsApp está faltando no config.json")

        self.debug = debug

    def send_whatsapp_message(self, text):
        """Envia mensagem de texto pelo WhatsApp via API do Facebook."""
        text = text[:4096]  # Limite do WhatsApp
        url = f"https://graph.facebook.com/v22.0/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": self.to_number,
            "type": "text",
            "text": {"body": text}
        }

        if self.debug:
            print("\n=== Enviando mensagem para WhatsApp ===")
            print(text)

        try:
            response = requests.post(url, headers=headers, json=payload)
            response_data = response.json() if response.ok else response.text
            success = response.ok

        except requests.RequestException as e:
            response_data = str(e)
            success = False

        if self.debug:
            print("\n=== Resposta da API do WhatsApp ===")
            print("✅ Sucesso!" if success else "❌ Falhou!")
            print("Resposta:", response_data)

        return {"success": success, "response": response_data}
