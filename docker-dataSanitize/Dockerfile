# Usa a imagem base do Python 3.11 slim
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala dependências do sistema que podem ser necessárias para compilar pacotes
RUN apt-get update && apt-get install -y \
    gcc \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo de dependências primeiro para otimizar o cache do Docker
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia a pasta de configuração e o código-fonte da aplicação
COPY config/ ./config/
COPY src/ ./src/

# Comando que inicia a aplicação worker
CMD ["python", "src/app.py"]