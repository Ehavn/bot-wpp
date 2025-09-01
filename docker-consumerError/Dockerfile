# Usa a imagem base do Python 3.11 slim
FROM python:3.11-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Instala dependências do sistema que podem ser necessárias para algumas bibliotecas Python
# É uma boa prática manter, caso futuras dependências precisem compilar código C.
RUN apt-get update && apt-get install -y \
    gcc \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 1. Copia o arquivo de dependências primeiro
COPY requirements.txt .

# 2. Instala as dependências logo em seguida
# Esta camada só será reconstruída se o 'requirements.txt' mudar.
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copia todo o restante do código do projeto
# Como as dependências já estão instaladas, esta etapa é muito mais rápida.
COPY . .

# 4. Comando que inicia o consumidor de erros
# Aponta para o 'app_error_handler.py' na raiz do projeto.
CMD ["python", "app_error_handler.py"]