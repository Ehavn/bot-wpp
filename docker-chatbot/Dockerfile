# --- Etapa 1: Build Stage ---
FROM python:3.11 as builder

WORKDIR /app

# Instala as dependências de compilação
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Cria um ambiente virtual
ENV VIRTUAL_ENV=/app/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copia e instala as dependências do Python no ambiente virtual
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Etapa 2: Final Stage ---
# Usamos uma imagem "slim" que é muito menor
FROM python:3.11-slim

WORKDIR /app

# Copia apenas o ambiente virtual com as dependências da etapa de build
COPY --from=builder /app/venv /app/venv

# Copia o código da aplicação
COPY . .

# Define o Python do ambiente virtual como o padrão
ENV PATH="/app/venv/bin:$PATH"

# Comando para executar a aplicação
CMD python -m src.app