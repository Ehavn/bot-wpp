Docker Consumer

Este serviço é responsável por consumir mensagens do RabbitMQ e armazená-las no MongoDB Atlas, aplicando um status inicial "pending" em cada registro inserido.

## 📂 Estrutura do projeto
.
├── config/
│   └── config.json         # Configurações do RabbitMQ e MongoDB
├── src/
│   ├── app.py              # Entrypoint principal
│   ├── rabbitmq_consumer.py # Lógica de consumo do RabbitMQ
│   ├── mongo_client.py     # Conexão com MongoDB
│   ├── logger.py           # Configuração centralizada de logs
├── requirements.txt        # Dependências Python
├── Dockerfile              # Configuração de build do container
└── README.md

## ⚙️ Configuração

O arquivo config/config.json contém as credenciais e parâmetros de conexão:

{
  "rabbitmq": {
    "host": "rabbitmq_host",
    "user": "guest",
    "password": "guest",
    "queue": "minha_fila"
  },
  "mongo": {
    "connectionUri": "mongodb+srv://usuario:senha@cluster.mongodb.net",
    "db_name": "meu_banco",
    "collection_raw": "raw_messages"
  }
}

## ▶️ Executando localmente
-  1. Criar ambiente virtual e instalar dependências
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

pip install -r requirements.txt

- 2. Iniciar o consumer
python src/app.py

## 🐳 Executando com Docker
- 1. Build da imagem
docker build -t docker-consumer .

- 2. Rodar o container
docker run --rm \
  -v $(pwd)/config:/app/config \
  --network="host" \
  docker-consumer


💡 O parâmetro --network="host" é útil quando RabbitMQ e MongoDB estão rodando localmente.
Caso use serviços externos (MongoDB Atlas, RabbitMQ em cloud), configure apenas no config.json.

## 📝 Logs

Os logs são enviados para o stdout do container, no formato:

2025-08-31 02:15:00 - INFO - Conexão com MongoDB Atlas estabelecida!
2025-08-31 02:15:05 - INFO - Conexão com RabbitMQ estabelecida!
2025-08-31 02:15:10 - INFO - Mensagem recebida: {"foo": "bar"}
2025-08-31 02:15:10 - INFO - Mensagem inserida no MongoDB com status 'pending'!

## 📌 Fluxo

O consumer aguarda mensagens na fila RabbitMQ.

Quando uma mensagem chega, ela é parseada em JSON.

O campo "status": "pending" é adicionado.

A mensagem é salva na coleção raw_messages do MongoDB.

O ack é enviado ao RabbitMQ confirmando o processamento.