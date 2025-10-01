import hmac
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

APP_SECRET = os.getenv("APP_SECRET")
PAYLOAD_FILE = "payload.json"
ENDPOINT_URL = "http://localhost:5000/"

if not APP_SECRET:
    print("Erro: APP_SECRET não encontrado no arquivo .env")
    exit(1)

try:
    with open(PAYLOAD_FILE, "rb") as f:
        payload_body = f.read()
except FileNotFoundError:
    print(f"Erro: Arquivo '{PAYLOAD_FILE}' não encontrado. Crie-o primeiro com o JSON de teste.")
    exit(1)

# Calcula a assinatura HMAC-SHA256
hashed = hmac.new(APP_SECRET.encode('utf-8'), payload_body, hashlib.sha256)
signature = hashed.hexdigest()
print(signature)