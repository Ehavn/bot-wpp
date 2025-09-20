# Dockerfile
# Etapa 1: Usar uma imagem base oficial e leve do Python
FROM python:3.11-slim

# Definir variáveis de ambiente para Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copiar o arquivo de dependências primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instalar as dependências do sistema e do Python
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove gcc && \
    rm -rf /var/lib/apt/lists/*

# Copiar o resto do código da aplicação
COPY . .

# Comando para executar a aplicação quando o container iniciar
# O worker será iniciado e ficará escutando a fila do RabbitMQ
CMD ["python", "app.py"]