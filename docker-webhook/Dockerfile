# Dockerfile Otimizado com Múltiplos Estágios

# ---- Estágio 1: Build ----
# Usamos uma imagem completa para instalar as dependências, que pode ser descartada depois.
FROM python:3.10 as builder

WORKDIR /usr/src/app

# Instala as dependências de forma segura em um ambiente virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copia e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Estágio 2: Final ----
# Usamos uma imagem 'slim' que é muito menor para a versão final.
FROM python:3.10-slim

ENV PYTHONUNBUFFERED True
WORKDIR /app

# Cria um usuário não-root para segurança
RUN useradd --create-home appuser
USER appuser

# Copia o ambiente virtual com as dependências do estágio de build
COPY --from=builder /opt/venv /opt/venv

# Copia o código da aplicação
COPY ./src .

# Define o caminho para usar os pacotes do ambiente virtual e executa a aplicação
ENV PATH="/opt/venv/bin:$PATH"
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 3 --worker-class gevent --threads 8 --timeout 0 src.app:app