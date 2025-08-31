# Usa a imagem base do Python 3.11 slim
FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema necessárias (para compilação de pacotes ou SSL)
RUN apt-get update && apt-get install -y \
    gcc \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia apenas requirements primeiro (para otimizar cache do Docker)
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia os arquivos do projeto
COPY config/ ./config/
COPY src/ ./src/

# Expõe a porta do Flask
EXPOSE 5000

# Comando que inicia a aplicação Flask (equivalente ao seu antigo main.py)
CMD ["python", "src/app.py"]
