# Usa a imagem base do Python 3.11 slim
FROM python:3.11-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Instala dependências do sistema que podem ser necessárias para algumas bibliotecas Python
RUN apt-get update && apt-get install -y \
    gcc \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo de dependências primeiro para aproveitar o cache do Docker
COPY requirements.txt ./

# Instala as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Copia os diretórios de código, configuração e documentos
COPY src/ ./src/
COPY config/ ./config/
COPY documentos/ ./documentos/
COPY app_ai.py ./

# Comando para iniciar a aplicação
CMD ["python", "app_ai.py"]