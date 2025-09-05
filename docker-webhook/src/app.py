from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from pika.exceptions import AMQPConnectionError
import hmac
import hashlib
from .utils.logger import get_logger
from .producer.rabbitmq import RabbitMQProducer
from .utils.validators import validate_whatsapp_payload

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configura o logger para este arquivo
logger = get_logger(__name__)

# Inicializa a aplicação Flask
app = Flask(__name__)

# Tenta carregar as configurações essenciais e conectar ao RabbitMQ ao iniciar
try:
    VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
    APP_SECRET = os.getenv("APP_SECRET")
    if not VERIFY_TOKEN or not APP_SECRET:
        raise ValueError("VERIFY_TOKEN e APP_SECRET devem ser definidos nas variáveis de ambiente.")
    
    logger.info("Tentando conectar ao RabbitMQ...")
    rabbit_producer = RabbitMQProducer()

except (ValueError, AMQPConnectionError) as e:
    # Se a inicialização falhar, o serviço não deve iniciar.
    logger.critical(
        "falha critica na inicializacao",
        extra={'error_message': str(e), 'error_type': type(e).__name__}
    )
    exit(1)

def verify_signature(request):
    """Verifica a assinatura HMAC SHA256 da requisição para garantir que ela veio do WhatsApp."""
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        logger.warning("requisicao sem assinatura", extra={'ip_address': request.remote_addr})
        return False
    
    sha_name, signature_hash = signature.split('=', 1)
    if sha_name != 'sha256':
        return False
    
    mac = hmac.new(APP_SECRET.encode(), request.data, hashlib.sha256)
    
    return hmac.compare_digest(signature_hash, mac.hexdigest())

@app.route("/", methods=["GET", "POST"])
def whatsapp_webhook():
    """Rota principal que lida com a verificação do webhook (GET) e o recebimento de notificações (POST)."""
    if request.method == "GET":
        # Lógica de verificação do webhook (quando você configura na plataforma da Meta)
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            logger.info("endpoint verificado com sucesso", extra={'hub_mode': mode})
            return challenge, 200
        else:
            logger.warning("falha na verificacao do endpoint", extra={'ip_address': request.remote_addr})
            return "Verification failed", 403

    if request.method == "POST":
        # Validação de segurança da assinatura
        if not verify_signature(request):
            logger.error("assinatura invalida", extra={'ip_address': request.remote_addr})
            return "Invalid signature", 403
        
        # Validação da estrutura do corpo da requisição
        dados = request.get_json()
        if not validate_whatsapp_payload(dados):
            logger.error(
                "payload invalido", 
                extra={
                    'ip_address': request.remote_addr, 
                    'payload_snippet': str(dados)[:200]
                }
            )
            return jsonify({"error": "Payload JSON inválido"}), 400

        try:
            # --- LÓGICA DE EXTRAÇÃO AJUSTADA PARA O PAYLOAD REAL ---
            messages = dados["value"]["messages"]
            for msg in messages:
                rabbit_producer.publish(msg)
            
            logger.info(
                "mensagens publicadas na fila", 
                extra={
                    'message_count': len(messages),
                    'wamid': messages[0].get('id'),
                    'recipient_phone': messages[0].get('from')
                }
            )
            return jsonify({"status": "ok"}), 200
        except Exception as e:
            logger.exception(
                "erro interno ao processar mensagens",
                extra={'error_message': str(e)}
            )
            return jsonify({"error": "Erro interno do servidor"}), 500
    
    return "Método não suportado", 405

if __name__ == "__main__":
    # Inicia a aplicação. As configurações de porta e debug são lidas das variáveis de ambiente.
    port = int(os.getenv("PORT", 5000))
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ('true', '1', 't')
    app.run(debug=debug_mode, port=port, host="0.0.0.0")