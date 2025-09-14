# Arquivo: Dockerfile (Para o projeto CONSUMER)

# --- Estágio 1: Build ---
FROM python:3.11-slim as builder

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Copia e instala as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Estágio 2: Final ---
FROM python:3.11-slim

WORKDIR /app

# Cria um usuário não-privilegiado
RUN useradd --create-home appuser
USER appuser

# Copia as dependências pré-instaladas
COPY --from=builder /usr/local /usr/local

# Copia o código-fonte
COPY --chown=appuser:appuser . .

# Define o PYTHONPATH para encontrar o módulo 'src'
ENV PYTHONPATH=/app

# Define o ponto de entrada padrão (pode ser sobrescrito pelo docker-compose)
ENV APP_ENTRYPOINT="src.app"

# Comando que inicia a aplicação worker (formato exec, mais seguro)
CMD python -m ${APP_ENTRYPOINT}
