# --- Estágio 1: Build ---
FROM python:3.11-slim as builder

WORKDIR /app

# Instala quaisquer dependências do sistema necessárias para compilar pacotes Python
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Copia o arquivo de dependências e instala os pacotes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Estágio 2: Final ---
FROM python:3.11-slim

WORKDIR /app

# Cria um usuário não-privilegiado para segurança
RUN useradd --create-home appuser
USER appuser

# Copia as dependências pré-instaladas do estágio de build
COPY --from=builder /usr/local /usr/local

# Copia o código-fonte
COPY --chown=appuser:appuser . .

# Define o PYTHONPATH para que o Python encontre o módulo 'src'
ENV PYTHONPATH=/app

# Copia e dá permissão de execução para o entrypoint
COPY --chown=appuser:appuser entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expõe a porta da aplicação
EXPOSE 5000

# Usa o entrypoint.sh para iniciar a aplicação
ENTRYPOINT ["/entrypoint.sh"]