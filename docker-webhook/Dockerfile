# Dockerfile Definitivo
FROM python:3.10-slim

ENV PYTHONUNBUFFERED True
WORKDIR /app

RUN useradd --create-home appuser
USER appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia toda a pasta src para o diretório de trabalho
COPY ./src .

# Executa a aplicação como um módulo, apontando para src.app
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 src.app:app