from flask import Flask, request, jsonify
import logging
import os
from dotenv import load_dotenv
from pika.exceptions import AMQPConnectionError
import hmac
import hashlib

from .producer.rabbitmq import RabbitMQProducer
from .utils.validators import validate_whatsapp_payload

# Carrega variáveis de ambiente do .env
load_dotenv()

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# --- INICIALIZAÇÃO SEGURA ---
try:
    # Carrega as configurações do ambiente
    VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
    APP_SECRET = os.getenv("APP_SECRET") # << NOVO! Você pega no painel do seu App no Facebook
    if not VERIFY_TOKEN or not APP_SECRET:
        raise ValueError("VERIFY_TOKEN e APP_SECRET devem ser definidos nas variáveis de ambiente.")
    
    logger.info("Tentando conectar ao RabbitMQ...")
    rabbit_producer = RabbitMQProducer()
    logger.info("Conexão com RabbitMQ estabelecida na inicialização.")

except (ValueError, AMQPConnectionError) as e:
    logger.critical("="*50)
    logger.critical("FALHA CRÍTICA NA INICIALIZAÇÃO DA APLICAÇÃO")
    logger.critical(f"ERRO: {e}")
    logger.critical("Verifique se o RabbitMQ está rodando e se as variáveis de ambiente (.env) estão corretas.")
    logger.critical("A aplicação será encerrada.")
    logger.critical("="*50)
    exit(1)

def verify_signature(request):
    """Verifica se a assinatura da requisição é válida."""
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        logger.warning("Requisição recebida sem a assinatura X-Hub-Signature-256.")
        return False

    sha_name, signature_hash = signature.split('=', 1)
    if sha_name != 'sha256':
        logger.warning(f"Algoritmo de assinatura não suportado: {sha_name}")
        return False

    # Calcula o hash HMAC da carga útil usando o App Secret
    mac = hmac.new(APP_SECRET.encode(), request.data, hashlib.sha256)
    
    # Compara os hashes de forma segura
    return hmac.compare_digest(signature_hash, mac.hexdigest())

@app.route("/", methods=["GET", "POST"])
def whatsapp_webhook():
    # ETAPA DE VERIFICAÇÃO DO ENDPOINT (só acontece uma vez)
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            logger.info("Endpoint verificado com sucesso!")
            return challenge, 200
        else:
            logger.warning("Falha na verificação do endpoint. Tokens não batem.")
            return "Verification failed", 403

    # ETAPA DE RECEBIMENTO DE MENSAGENS (acontece sempre)
    if request.method == "POST":
        # 1. VERIFICA A ASSINATURA (NOVO MÉTODO DE SEGURANÇA)
        if not verify_signature(request):
            logger.error("Assinatura inválida. A requisição pode ser maliciosa ou mal configurada.")
            return "Invalid signature", 403
        
        # O resto do seu código continua igual...
        dados = request.get_json()
        if not validate_whatsapp_payload(dados):
            logger.error(f"Payload inválido recebido: {dados}")
            return jsonify({"error": "Payload JSON inválido ou malformatado"}), 400

        try:
            messages = dados["entry"][0]["changes"][0]["value"]["messages"]
            for msg in messages:
                rabbit_producer.publish(msg)
            
            logger.info(f"{len(messages)} mensagem(ns) publicada(s) com sucesso na fila.")
            return jsonify({"status": "ok"}), 200
        except Exception as e:
            logger.exception("Erro interno ao processar e publicar mensagens")
            return jsonify({"error": "Erro interno do servidor"}), 500
    
    return "Método não suportado", 405

# --- EXECUÇÃO EM PRODUÇÃO ---
# Para produção, use um servidor WSGI como Gunicorn:
# gunicorn --bind 0.0.0.0:5000 app:app
#
# A linha abaixo é apenas para desenvolvimento local.
if __name__ == "__main__":
    # Nunca use debug=True em produção!
    app.run(debug=False, port=5000, host="0.0.0.0")