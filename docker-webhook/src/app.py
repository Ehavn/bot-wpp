<<<<<<< HEAD
from flask import Flask, request, jsonify
import logging
from src.rabbitmq import publish_message

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/", methods=["POST"])
def whatsapp_webhook():
    try:
        dados = request.get_json(force=True, silent=True)
        if not dados:
            return jsonify({"error": "JSON inválido"}), 400

        value = dados.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            return jsonify({"status": "sem mensagens"}), 200

        for msg in messages:
            publish_message(msg)

        logger.info(f"{len(messages)} mensagem(ns) publicada(s) na fila.")
        return jsonify({"status": "ok", "count": len(messages)}), 200

    except Exception as e:
        logger.exception("Erro ao processar webhook")
        return jsonify({"error": "erro interno"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
=======
from flask import Flask, request, jsonify
import logging
from src.rabbitmq import publish_message

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/", methods=["POST"])
def whatsapp_webhook():
    try:
        dados = request.get_json(force=True, silent=True)
        if not dados:
            return jsonify({"error": "JSON inválido"}), 400

        value = dados.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            return jsonify({"status": "sem mensagens"}), 200

        for msg in messages:
            publish_message(msg)

        logger.info(f"{len(messages)} mensagem(ns) publicada(s) na fila.")
        return jsonify({"status": "ok", "count": len(messages)}), 200

    except Exception as e:
        logger.exception("Erro ao processar webhook")
        return jsonify({"error": "erro interno"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
>>>>>>> cccf66339631c294e783b616174331c055f49216
