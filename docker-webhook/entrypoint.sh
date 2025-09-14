#!/bin/sh

# entrypoint.sh - Script para iniciar a aplicação Gunicorn com workers dinâmicos.

# Define um valor padrão para a porta se não for fornecida.
PORT=${PORT:-5000}

# Calcula o número de núcleos de CPU disponíveis na máquina ou no contêiner.
CORES=$(nproc)

# Calcula o número de workers Gunicorn com base na fórmula recomendada: (2 * NÚCLEOS) + 1.
WORKERS=$((2 * CORES + 1))

echo "========================================================================="
echo "Iniciando a Aplicação..."
echo "Número de núcleos de CPU detectados: $CORES"
echo "Número de workers Gunicorn calculados: $WORKERS"
echo "Aplicação será exposta na porta: $PORT"
echo "========================================================================="

# Executa o Gunicorn com as configurações otimizadas.
exec gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers $WORKERS \
    --worker-class gevent \
    --threads 8 \
    --timeout 60 \
    src.app:app
