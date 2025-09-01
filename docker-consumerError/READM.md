# Aplicação de Gerenciamento de Erros

Este serviço é responsável por capturar, armazenar e gerenciar mensagens que falharam no processamento do consumidor principal. Ele oferece ferramentas para análise e recuperação de falhas.

## Componentes

1.  **Consumidor de Erros (`app_error_handler.py`):**
    Um serviço que roda em background, escuta a fila de erros do RabbitMQ (`failed_messages`) e salva cada mensagem falha em uma coleção do MongoDB (`dead_letter_messages`) para análise posterior.

2.  **Ferramenta de Gestão (`manage.py`):**
    Uma interface de linha de comando (CLI) para interagir com as mensagens que falharam.

## Como Usar

### 1. Rodar o Consumidor de Erros
Este serviço deve ficar rodando continuamente para capturar qualquer erro que aconteça.

```bash
python app_error_handler.py
2. Gerenciar Mensagens com Falha (CLI)
Use este script em outro terminal para executar ações.

Listar todas as mensagens com erro não resolvidas:

Bash

python manage.py list
Ver o detalhe de uma mensagem específica (use o ID da lista anterior):

Bash

python manage.py show 63d1a8b1c4e9f7b6d4f9c3e2
Tentar processar uma mensagem novamente (reenfileirar):

Bash

python manage.py retry 63d1a8b1c4e9f7b6d4f9c3e2
Descartar uma mensagem que não pode ser processada:

Bash

python manage.py discard 63d1a8b1c4e9f7b6d4f9c3e2