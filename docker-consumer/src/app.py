from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    print("Webhook recebido:", data)
    return jsonify({"status": "success"}), 200
