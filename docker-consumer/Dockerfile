# Usa a imagem base do Python 3.11 slim
FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema necessárias para compilação de pacotes
RUN apt-get update && apt-get install -y \
    gcc \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo de dependências primeiro para otimizar o cache
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia os arquivos do projeto para o container
COPY config/ ./config/
COPY src/ ./src/

# Comando que inicia a aplicação consumidora
CMD ["python", "src/app.py"]