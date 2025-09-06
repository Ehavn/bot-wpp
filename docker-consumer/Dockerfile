# Dockerfile

# ---- Estágio 1: Build ----
# Usamos uma imagem completa para instalar as dependências
FROM python:3.11 as builder

WORKDIR /usr/src/app

# Cria e ativa um ambiente virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instala as dependências de forma otimizada
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ---- Estágio 2: Final ----
# Usamos uma imagem 'slim' para a versão final
FROM python:3.11-slim

# Evita que o Python gere arquivos .pyc e bufferize logs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Cria um usuário não-root para máxima segurança
RUN useradd --create-home appuser
USER appuser

# Copia o ambiente virtual com as dependências do estágio de build
COPY --from=builder /opt/venv /opt/venv

# Copia apenas o código-fonte necessário para a execução
COPY --chown=appuser:appuser src/ ./src
COPY --chown=appuser:appuser app.py .

# Define o caminho para usar os pacotes do ambiente virtual
ENV PATH="/opt/venv/bin:$PATH"

# Comando para executar a aplicação.
# O app.py agora inicia apenas um processo, que é o ideal para contêineres.
CMD ["python", "app.py"]