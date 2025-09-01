<<<<<<< HEAD
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

# Copia os arquivos do projeto
COPY config/ ./config/
COPY src/ ./src/

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Comando que inicia o consumidor
CMD ["python", "src/app.py"]
=======
# Usa a imagem base do Python 3.11 slim
FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema necessárias (para compilação de pacotes ou SSL)
RUN apt-get update && apt-get install -y \
    gcc \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia arquivos do projeto
COPY requirements.txt ./
COPY main.py ./
COPY logger.py ./
COPY utils/ ./utils/
COPY config/ ./config/

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Comando que inicia o consumidor
CMD ["python", "main.py"]
>>>>>>> cccf66339631c294e783b616174331c055f49216
