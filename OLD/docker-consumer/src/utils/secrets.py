# src/utils/secrets.py
import os
from google.cloud import secretmanager

PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

def get_secret(secret_key: str) -> str:
    """
    Busca um segredo. Em produção, busca no Google Secret Manager.
    Retorna None se não estiver em produção, para que o Pydantic possa usar o .env.
    """
    if ENVIRONMENT != "production":
        # Em ambiente local, não fazemos nada. O Pydantic cuidará de ler o .env.
        # Ele precisa retornar None para que o Pydantic saiba que deve procurar em outro lugar.
        return None

    if not PROJECT_ID:
        raise ValueError("A variável de ambiente 'GOOGLE_PROJECT_ID' é necessária em produção.")

    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{PROJECT_ID}/secrets/{secret_key}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        raise RuntimeError(f"Crítico: Não foi possível acessar o segredo '{secret_key}' no Google Secret Manager.") from e