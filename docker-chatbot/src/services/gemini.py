# services/gemini.py
import json
import google.generativeai as genai

# Em: src/services/gemini.py

class GeminiConnector:
    def __init__(self, config_file="config/config.json"):
        with open(config_file, "r") as f:
            config = json.load(f)

        gemini_config = config.get("gemini", {})
        self.api_key = gemini_config.get("api_key")
        if not self.api_key:
            raise ValueError("gemini.api_key não encontrado no config.json")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

        # --- MUDANÇA PRINCIPAL AQUI ---
        # Ajuste a estrutura para o formato do Gemini
        self.diretrizes = [
            {
                "role": "user", 
                "parts": [{"text": "Você é um assistente corretor de seguros. Seja sempre educado, direto e prestativo."}]
            },
            {
                "role": "model",
                "parts": [{"text": "Entendido. Atuarei como um corretor de seguros, sendo educado, direto e prestativo."}]
            }
        ]
        
        self.chat = self.model.start_chat(history=self.diretrizes)
    
    # O resto da sua classe (método enviar_mensagem) continua igual...


    def enviar_mensagem(self, mensagem_usuario: str, contexto: str = None) -> str:
        """
        Envia mensagem para a IA, opcionalmente com um contexto extra.
        """
        # Reinicia o chat para garantir que o contexto seja aplicado apenas a esta conversa
        self.chat = self.model.start_chat(history=self.diretrizes)
        
        prompt_final = mensagem_usuario
        if contexto:
            prompt_final = f"Use o seguinte contexto para responder à pergunta: \n--- CONTEXTO ---\n{contexto}\n--- FIM DO CONTEXTO ---\n\nPergunta do usuário: {mensagem_usuario}"

        resposta = self.chat.send_message(prompt_final)
        return resposta.text