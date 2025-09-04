# Arquivo: src/services/gemini.py

import json
import google.generativeai as genai

class GeminiConnector:
    def __init__(self, config_file="config/config.json"):
        with open(config_file, "r") as f:
            config = json.load(f)

        gemini_config = config.get("gemini", {})
        self.api_key = gemini_config.get("api_key")
        if not self.api_key:
            raise ValueError("gemini.api_key não encontrado no config.json")

        genai.configure(api_key=self.api_key)
        # O modelo é configurado com as instruções de sistema a cada chamada

    # --- MÉTODO FINAL E CORRIGIDO ---
    def enviar_mensagem(self, historico_formatado: list) -> str:
        """
        Recebe um histórico de conversa completo, incluindo instruções de sistema,
        e gera a próxima resposta usando o método mais robusto.
        """
        try:
            # Extrai a instrução de sistema da lista
            instrucao_sistema = next((h["parts"][0]["text"] for h in historico_formatado if h["role"] == "system"), None)
            
            # Filtra a lista para conter apenas a conversa (user/model)
            mensagens_conversa = [h for h in historico_formatado if h["role"] != "system"]

            # Cria uma instância do modelo com as instruções de sistema
            modelo_com_instrucao = genai.GenerativeModel(
                "gemini-1.5-flash",
                system_instruction=instrucao_sistema
            )

            # Gera o conteúdo baseado na conversa
            resposta = modelo_com_instrucao.generate_content(mensagens_conversa)
            return resposta.text
        
        except Exception as e:
            print(f"ERRO na chamada da API do Gemini: {e}")
            return "Desculpe, ocorreu um erro ao tentar processar sua solicitação."