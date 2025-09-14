# Arquivo: src/app.py (Ajustado)

# --- ADICIONE ESTAS DUAS LINHAS NO TOPO DO ARQUIVO ---
from dotenv import load_dotenv
load_dotenv()
# ---------------------------------------------------

from flask import Flask, request, jsonify
# ... resto dos seus imports e código do Flask ...

# Exemplo de como seu app pode estar estruturado
app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    # Sua lógica de webhook aqui...
    data = request.json
    print("Webhook recebido:", data)
    # Aqui você usaria o Pika para enviar a mensagem para o RabbitMQ
    return jsonify({"status": "success"}), 200

# O Gunicorn encontrará e executará esta variável 'app'.
# Você não precisa de um bloco if __name__ == '__main__' para o Gunicorn.