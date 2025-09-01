# 📲 WhatsApp Chatbot Webhook

Este projeto implementa um **webhook em Flask** que recebe mensagens do WhatsApp e as publica em uma fila **RabbitMQ**, onde outros serviços (como sanitização, IA e armazenamento) podem consumir e processar os dados.

---

## 📂 Estrutura do Projeto

DOCKER-WEBHOOK/
│── config/
│ └── config.json # Configurações do projeto
│── src/
│ ├── app.py # Flask App (Webhook principal)
│ ├── rabbitmq.py # Funções de integração com RabbitMQ
│ └── utils.py # Funções auxiliares (validação, logs)
│── requirements.txt # Dependências Python
│── Dockerfile # Build do container
│── README.md # Este arquivo :)


---

## 🚀 Como funciona

1. O **Flask (app.py)** expõe um endpoint `/` que recebe mensagens do WhatsApp.
2. Cada mensagem recebida é validada e publicada em uma fila no **RabbitMQ**.
3. O **RabbitMQ** garante persistência e distribuição das mensagens para serviços consumidores (workers).
4. Futuramente, workers podem:
   - Armazenar mensagens no **MongoDB** (RAW e sanitizadas).
   - Salvar relatórios e leads no **Postgres**.
   - Invocar a **IA (Gemini)** para responder conversas.

---

## ⚙️ Configuração

### Arquivo `config/config.json`

```json
{
  "rabbitmq": {
    "host": "localhost",
    "user": "guest",
    "password": "guest",
    "queue": "whatsapp_queue"
  },
  "flask": {
    "port": 5000,
    "debug": true
  }
}
🔒 Em produção, recomenda-se usar variáveis de ambiente em vez de config.json.

🐳 Rodando com Docker
Build da imagem
docker build -t whatsapp-webhook .

Rodar o container
docker run -d \
  --name whatsapp-webhook \
  -p 5000:5000 \
  --env RABBIT_HOST=host.docker.internal \
  --env RABBIT_USER=guest \
  --env RABBIT_PASS=guest \
  --env RABBIT_QUEUE=whatsapp_queue \
  whatsapp-webhook

📬 Testando o Webhook

Envie um POST para o endpoint:

curl -X POST http://localhost:5000/ \
  -H "Content-Type: application/json" \
  -d '{
    "value": {
      "messages": [
        {"id": "msg1", "from": "5511999999999", "text": {"body": "Olá"}}
      ]
    }
  }'


Resposta esperada:

{
  "status": "ok",
  "count": 1
}


E a mensagem aparecerá no RabbitMQ.

🔮 Próximos passos

Implementar worker consumidor que lê mensagens da fila.

Armazenar mensagens RAW e sanitizadas em MongoDB.

Salvar leads e relatórios em Postgres.

Integrar IA (Gemini) para respostas automáticas.

Configurar docker-compose.yml para orquestrar Webhook + RabbitMQ + Workers.

📜 Licença

Projeto interno para estudo e prototipagem.


---

👉 Quer que eu já adicione ao README um **docker-compose.yml de exemplo** (Webhook + RabbitMQ), assim você consegue subir tudo com um único `docker compose up`?
