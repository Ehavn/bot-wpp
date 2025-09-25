import os
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
from src.utils.logger import get_logger

logger = get_logger("GeminiConnector")

class GeminiConnector:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("A variável de ambiente GEMINI_API_KEY não foi definida.")
        
        genai.configure(api_key=self.api_key)
        logger.info("Gemini Connector inicializado.")

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True
    )
    def enviar_mensagem(self, historico_formatado: list) -> str:
        """
        Envia a conversa para a API do Gemini, com retentativas em caso de falha.
        """
        try:
            instrucao_sistema = next((h["parts"][0]["text"] for h in historico_formatado if h["role"] == "system"), None)
            mensagens_conversa = [h for h in historico_formatado if h["role"] != "system"]

            modelo = genai.GenerativeModel(
                "gemini-1.5-flash",
                system_instruction=instrucao_sistema
            )

            resposta = modelo.generate_content(mensagens_conversa)
            return resposta.text
        
        except Exception as e:
            logger.error(f"Erro na chamada da API do Gemini: {e}", exc_info=True)
            raise