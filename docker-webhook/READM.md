## 📲 WhatsApp Chatbot Webhook
Este projeto implementa um webhook em Flask que recebe mensagens do WhatsApp e as publica em uma fila RabbitMQ, onde outros serviços (como sanitização, IA e armazenamento) podem consumir e processar os dados.

## 📂 Estrutura do Projeto
DOCKER-WEBHOOK/
│── config/
│   └── config.json       # Configurações do projeto
│── src/
│   ├── app.py            # Flask App (Webhook principal)
│   ├── rabbitmq.py       # Funções de integração com RabbitMQ
│   └── logger.py         # Funções auxiliares (neste caso, `utils.py`)
│── requirements.txt      # Dependências Python
│── Dockerfile            # Build do container
└── README.md             # Este arquivo
## 🚀 Como funciona
O Flask (app.py) expõe um endpoint / que recebe notificações de mensagens do WhatsApp via POST.

Cada mensagem recebida é extraída e publicada individualmente em uma fila no RabbitMQ.

O RabbitMQ atua como um message broker, garantindo a persistência e a distribuição das mensagens para os serviços consumidores (workers).

Futuramente, workers poderão ser implementados para:

Armazenar mensagens no MongoDB (dados brutos e sanitizados).

Salvar relatórios e leads em um banco de dados relacional como o Postgres.

Invocar uma IA (Gemini) para analisar e responder às conversas.

## ⚙️ Configuração
Arquivo config/config.json
O arquivo de configuração define os parâmetros de conexão para o RabbitMQ e as configurações do servidor Flask.

JSON

{
  "rabbitmq": {
    "host": "localhost",
    "user": "admin",
    "password": "admin",
    "queue": "new_messages"
  },
  "flask": {
    "port": 5000,
    "debug": true
  }
}
🔒 Nota de Segurança: Em um ambiente de produção, é altamente recomendável utilizar variáveis de ambiente para gerenciar credenciais e configurações sensíveis, em vez de um arquivo config.json.

## 🐳 Rodando com Docker
- 1. Build da imagem
Execute o comando a seguir na raiz do projeto para construir a imagem Docker.

Bash

docker build -t whatsapp-webhook .
- 2. Rodar o container
Para iniciar o container, use o comando abaixo. Lembre-se de substituir os valores das variáveis de ambiente (RABBIT_HOST, RABBIT_USER, etc.) pelos dados corretos do seu broker RabbitMQ.

Bash

docker run -d \
  --name whatsapp-webhook \
  -p 5000:5000 \
  --env RABBIT_HOST=host.docker.internal \
  --env RABBIT_USER=admin \
  --env RABBIT_PASS=admin \
  --env RABBIT_QUEUE=new_messages \
  whatsapp-webhook
Nota: O valor host.docker.internal para RABBIT_HOST permite que o container Docker se conecte a um serviço (RabbitMQ) que está rodando na sua máquina host.

## 📬 Testando o Webhook
Após iniciar o container, você pode enviar um evento de teste para o endpoint usando curl:

Bash

curl -X POST http://localhost:5000/ \
  -H "Content-Type: application/json" \
  -d '{
    "value": {
      "messages": [
        {"id": "msg1", "from": "5511999999999", "text": {"body": "Olá, tudo bem?"}},
        {"id": "msg2", "from": "5521888888888", "text": {"body": "Gostaria de um orçamento."}}
      ]
    }
  }'
Resposta esperada:
O webhook retornará uma confirmação com o número de mensagens publicadas na fila.

JSON

{
  "status": "ok",
  "count": 2
}
Após o teste, as duas mensagens aparecerão na fila new_messages do seu RabbitMQ.