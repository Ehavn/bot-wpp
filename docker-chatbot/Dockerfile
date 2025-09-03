# --- Estágio 1: Builder ---
# Usa uma imagem completa para instalar as dependências
FROM python:3.11 as builder

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema que podem ser necessárias para compilar pacotes
RUN apt-get update && apt-get install -y \
    gcc \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Instala as dependências Python em um local isolado
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix="/install" -r requirements.txt


# --- Estágio 2: Final ---
# Usa uma imagem "slim" para a imagem final, que é muito menor
FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Cria um usuário não-root para rodar a aplicação (boa prática de segurança)
RUN addgroup --system nonroot && adduser --system --group nonroot
USER nonroot

# Copia as dependências já instaladas do estágio "builder"
COPY --from=builder /install /usr/local

# Copia os arquivos da aplicação
COPY --chown=nonroot:nonroot config/ ./config/
COPY --chown=nonroot:nonroot src/ ./src/
COPY --chown=nonroot:nonroot app.py .

# Comando que inicia a aplicação
CMD ["python", "app.py"]