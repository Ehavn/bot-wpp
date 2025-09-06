from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from pika.exceptions import AMQPConnectionError
import hmac
import hashlib
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .utils.logger import get_logger
from .producer.rabbitmq import RabbitMQProducer
from .utils.validators import validate_whatsapp_payload

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configura o logger para este arquivo
logger = get_logger(__name__)

# Inicializa a aplicação Flask
app = Flask(__name__)

# --- Configuração do Rate Limiter (Ajustado) ---
limiter = Limiter(
    get_remote_address, # Usa o endereço de IP como chave
    app=app,
    default_limits=["20 per second"], # Define o limite padrão para 20 requisições por segundo
    storage_uri=os.getenv("RATE_LIMIT_STORAGE_URI", "memory://")
)

# Tenta carregar as configurações essenciais e conectar ao RabbitMQ ao iniciar
try:
    VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
    APP_SECRET = os.getenv("APP_SECRET")
    if not VERIFY_TOKEN or not APP_SECRET:
        raise ValueError("VERIFY_TOKEN e APP_SECRET devem ser definidos nas variáveis de ambiente.")
    
    logger.info("Tentando conectar ao RabbitMQ...")
    rabbit_producer = RabbitMQProducer()

except (ValueError, AMQPConnectionError) as e:
    logger.critical(
        "falha critica na inicializacao",
        extra={'error_message': str(e), 'error_type': type(e).__name__}
    )
    exit(1)

def verify_signature(request):
    """Verifica a assinatura HMAC SHA256 da requisição."""
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        logger.warning("requisicao sem assinatura", extra={'ip_address': request.remote_addr})
        return False
    
    sha_name, signature_hash = signature.split('=', 1)
    if sha_name != 'sha256':
        return False
    
    mac = hmac.new(APP_SECRET.encode(), request.data, hashlib.sha256)
    
    return hmac.compare_digest(signature_hash, mac.hexdigest())

@app.route("/health", methods=["GET"])
@limiter.exempt # Isenta o health check dos limites de taxa
def health_check():
    """Endpoint simples para verificação de saúde (health check)."""
    return jsonify({"status": "healthy"}), 200

@app.route("/", methods=["GET", "POST"])
# Esta rota agora usará o limite padrão de "20 per second" definido acima
def whatsapp_webhook():
    """Rota principal que lida com o webhook do WhatsApp."""
    if request.method == "GET":
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
        if not verify_signature(request):
            logger.error("assinatura invalida", extra={'ip_address': request.remote_addr})
            return "Invalid signature", 403
        
        try:
            dados = request.get_json()
        except Exception as e:
            logger.error(
                "falha ao fazer o parse do json", 
                extra={'error_message': str(e), 'ip_address': request.remote_addr}
            )
            return jsonify({"error": "JSON malformado ou Content-Type inválido."}), 400
        
        if not validate_whatsapp_payload(dados):
            logger.error(
                "payload invalido", 
                extra={'ip_address': request.remote_addr, 'payload_snippet': str(dados)[:200]}
            )
            return jsonify({"error": "Payload JSON inválido"}), 400

        try:
            # 1. Extrai a lista de mensagens do payload
            messages_to_publish = dados["value"]["messages"]

            # 2. Publica a LISTA inteira como uma única mensagem
            rabbit_producer.publish(messages_to_publish)
            
            # 3. Atualiza o log para refletir a ação
            logger.info(
                "lista de mensagens publicada na fila com sucesso", 
                extra={'message_count': len(messages_to_publish)}
            )
            return jsonify({"status": "Recebido Com Sucesso"}), 200
        except Exception as e:
            logger.exception(
                "erro interno ao processar mensagens",
                extra={'error_message': str(e)}
            )
            return jsonify({"error": "Erro interno do servidor"}), 500
    
    return "Método não suportado", 405

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ('true', '1', 't')
    app.run(debug=debug_mode, port=port, host="0.0.0.0")