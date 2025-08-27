import json
import google.generativeai as genai

class GeminiConnector:
    def __init__(self, config_file="config/config.json"):
        # Carrega config
        with open(config_file, "r") as f:
            config = json.load(f)

        gemini_config = config.get("gemini", {})
        self.api_key = gemini_config.get("api_key")
        if not self.api_key:
            raise ValueError("gemini.api_key não encontrado no config.json")

        # Configura Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

        # Diretrizes iniciais
        self.diretrizes = [
            {"role": "system", "content": "Você é um assistente corretor de seguros e útil. Sempre seja educado e direto."},
            {"role": "system", "content": "Responda de forma concisa, evitando informações irrelevantes e nem fugindo do assunto, voltando para o tema de forma respeitosa se necessário."},
            {"role": "system", "content": "Nunca informe dados sensíveis, como documentos ou acessos restritos."}
        ]

        # Inicializa o chat com as diretrizes
        self.chat = self.model.start_chat(history=self.diretrizes)

    def enviar_mensagem(self, mensagem: str, diretrizes_extras: list[str] = None) -> str:
        """
        Envia mensagem para a IA.
        diretrizes_extras: lista de strings que serão enviadas como 'system' antes da mensagem do usuário
        """
        if diretrizes_extras:
            for diretriz in diretrizes_extras:
                self.chat.send_message(diretriz, role="system")
        resposta = self.chat.send_message(mensagem)
        return resposta.text
