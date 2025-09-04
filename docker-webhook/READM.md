# 📲 WhatsApp Webhook com RabbitMQ

Este projeto implementa um webhook seguro em Flask que recebe notificações do WhatsApp, valida os dados e os publica de forma assíncrona em uma fila RabbitMQ.

## 📂 Estrutura do Projeto (Segura)

DOCKER-WEBHOOK/
│
├── src/
│   ├── /producer
│   │   └── rabbitmq.py       # Lógica de publicação no RabbitMQ
│   └── /utils
│       └── validators.py     # Funções de validação de payload
│
├── .env                    # Arquivo de segredos e configurações (NÃO versionado)
├── .gitignore              # Arquivos e pastas a serem ignorados pelo Git
├── app.py                  # Aplicação Flask (Webhook principal)
├── requirements.txt        # Dependências Python
├── Dockerfile              # Build do contêiner para produção
└── README.md               # Este arquivo

## ⚙️ Configuração com Variáveis de Ambiente

Este projeto é configurado exclusivamente via variáveis de ambiente para máxima segurança, seguindo a metodologia Twelve-Factor App. Para desenvolvimento local, crie um arquivo `.env` na raiz do projeto:

```ini
# Configurações do RabbitMQ
RABBIT_HOST=localhost
RABBIT_USER=admin
RABBIT_PASS=admin
QUEUE_NAME=new_messages

# Configurações do Flask
FLASK_PORT=5000
FLASK_DEBUG=False # Sempre False em produção

# Segredo de Autenticação do Webhook
WEBHOOK_TOKEN=seu_token_longo_e_secreto_aqui

## 🐳 Rodando com Docker
1. Build da Imagem

Bash

docker build -t whatsapp-webhook .
2. Rodar o Contêiner
Para iniciar, use o comando abaixo, substituindo os valores das variáveis de ambiente (--env) pelos dados corretos do seu ambiente.

Bash

docker run -d \
  --name whatsapp-webhook \
  -p 5000:5000 \
  --env RABBIT_HOST=host.docker.internal \
  --env RABBIT_USER=admin \
  --env RABBIT_PASS=admin \
  --env QUEUE_NAME=new_messages \
  --env WEBHOOK_TOKEN=seu_token_longo_e_secreto_aqui \
  whatsapp-webhook
  
## 📬 Testando o Webhook (com Segurança)
Após iniciar o contêiner, envie um evento de teste para o endpoint usando curl, incluindo o WEBHOOK_TOKEN no cabeçalho Authorization.

Bash

curl -X POST http://localhost:5000/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer seu_token_longo_e_secreto_aqui" \
  -d '{
    "value": {
      "messages": [
        {"id": "msg1", "from": "5511999999999", "text": {"body": "Olá, tudo bem?"}},
        {"id": "msg2", "from": "5521888888888", "text": {"body": "Gostaria de um orçamento."}}
      ]
    }
  }'
