from flask import Flask, request, jsonify
import pika
import json

with open("config/config.json", "r") as f:
    config = json.load(f)

RABBIT_HOST = config["rabbitmq"]["host"]
RABBIT_USER = config["rabbitmq"]["user"]
RABBIT_PASS = config["rabbitmq"]["password"]
QUEUE_NAME = config["rabbitmq"]["queue"]

FLASK_PORT = config["flask"]["port"]
FLASK_DEBUG = config["flask"]["debug"]

app = Flask(__name__)

# Conexão com RabbitMQ
credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
parameters = pika.ConnectionParameters(host=RABBIT_HOST, credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Declara a fila
channel.queue_declare(queue=QUEUE_NAME, durable=True)

# Rota do webhook
@app.route("/", methods=["POST"])
def whatsapp_webhook():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "JSON inválido"}), 400

        value = dados.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            return jsonify({"status": "sem mensagens"}), 200

        # Publica cada mensagem na fila
        for msg in messages:
            channel.basic_publish(
                exchange='',
                routing_key=QUEUE_NAME,
                body=json.dumps(msg),
                properties=pika.BasicProperties(
                    delivery_mode=2  # torna a mensagem persistente
                )
            )

        print(f"{len(messages)} mensagem(ns) publicada(s) na fila.")
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Erro:", e)
        return jsonify({"error": "erro interno"}), 500

if __name__ == "__main__":
    app.run(debug=FLASK_DEBUG, port=FLASK_PORT)
