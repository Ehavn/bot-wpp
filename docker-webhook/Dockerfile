# Dockerfile Otimizado com Múltiplos Estágios e Workers Dinâmicos

# ---- Estágio 1: Build ----
# Usamos uma imagem completa para instalar as dependências.
FROM python:3.10 as builder

WORKDIR /usr/src/app

# Instala as dependências em um ambiente virtual.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copia o arquivo de lock para garantir builds 100% reproduzíveis.
COPY requirements.lock .
# Instala as dependências a partir do arquivo de lock.
RUN pip install --no-cache-dir -r requirements.lock


# ---- Estágio 2: Final ----
# Usamos uma imagem 'slim' que é muito menor para a versão final.
FROM python:3.10-slim

ENV PYTHONUNBUFFERED True
WORKDIR /app

# Cria um usuário não-root para segurança.
RUN useradd --create-home appuser

# Copia o ambiente virtual com as dependências do estágio de build.
COPY --from=builder /opt/venv /opt/venv

# Copia o código da aplicação e o script de entrypoint.
COPY ./src .
COPY entrypoint.sh .

# Garante que o usuário 'appuser' seja o dono dos arquivos
# e que o entrypoint seja executável.
RUN chown -R appuser:appuser /app && \
    chmod +x /app/entrypoint.sh

# Muda para o usuário não-root.
USER appuser

# Define o caminho para usar os pacotes do ambiente virtual.
ENV PATH="/opt/venv/bin:$PATH"

# Define o entrypoint que será executado quando o contêiner iniciar.
# Ele irá calcular os workers e iniciar o Gunicorn.
ENTRYPOINT ["/app/entrypoint.sh"]