## 📥 Docker Consumer - RabbitMQ to MongoDB
Este serviço atua como um consumidor, responsável por processar mensagens de uma fila RabbitMQ e armazená-las de forma segura em um banco de dados MongoDB Atlas. Cada mensagem recebida é enriquecida com um status inicial "pending" antes de ser persistida.

## 📂 Estrutura do Projeto
.
├── config/
│   └── config.json         # Configurações do RabbitMQ e MongoDB
├── src/
│   ├── app.py              # Entrypoint principal que inicia o consumidor
│   ├── consumer/
│   │   └── rabbitmq_consumer.py # Lógica de consumo e inserção no MongoDB
│   └── utils/
│       ├── mongo_client.py     # Lógica de conexão com MongoDB
│       └── logger.py           # Configuração de logs
├── requirements.txt        # Dependências Python
├── Dockerfile              # Configuração de build do container
└── README.md
## ⚙️ Configuração
O arquivo config/config.json centraliza todos os parâmetros de conexão.

JSON

{
  "rabbitmq": {
    "host": "localhost",
    "user": "admin",
    "password": "admin",
    "queue": "new_messages",
    "queue_error": "failed_messages"
  },
  "mongo": {
    "connectionUri": "mongodb+srv://ehavn:1951@cluster-chatbot.npckgpy.mongodb.net/?retryWrites=true&w=majority&appName=Cluster-chatbot",
    "db_name": "messages",
    "collection_raw": "raw"
  }
}
## ▶️ Executando Localmente
Criar ambiente virtual e instalar dependências:

Bash

### Criar e ativar o ambiente virtual
python -m venv venv
source venv/bin/activate   # Linux/Mac
### venv\Scripts\activate      # Windows

### Instalar pacotes
pip install -r requirements.txt
Iniciar o consumidor:

Bash

python src/app.py
🐳 Executando com Docker
Build da imagem Docker:

Bash

docker build -t rabbitmq-consumer .
Rodar o container:
Para conectar o container a um serviço RabbitMQ rodando na sua máquina host (localhost), use a flag --network="host".

Bash

docker run --rm --name consumer-instance \
  -v $(pwd)/config:/app/config \
  --network="host" \
  rabbitmq-consumer
💡 Nota: O uso de --network="host" é ideal para desenvolvimento local. Em produção, você normalmente usaria uma rede Docker customizada (docker network create ...) ou se conectaria a serviços de nuvem (como CloudAMQP e MongoDB Atlas), onde a configuração no config.json seria suficiente.

## 📝 Logs
Os logs são enviados para a saída padrão (stdout) do container, permitindo fácil monitoramento com docker logs.

Exemplo de saída:

2025-09-03 18:00:00 - INFO - Iniciando consumidor...
2025-09-03 18:00:01 - INFO - Conexão com MongoDB Atlas estabelecida!
2025-09-03 18:00:06 - INFO - Conexão com RabbitMQ estabelecida!
2025-09-03 18:00:06 - INFO - Consumidor iniciado, aguardando mensagens...
2025-09-03 18:00:15 - INFO - Mensagem recebida: {'id': 'msg1', 'from': '5511...'}
2025-09-03 18:00:15 - INFO - Mensagem inserida no MongoDB com status 'pending'!

## 📌 Fluxo de Processamento
O consumidor estabelece conexões contínuas com o RabbitMQ e o MongoDB Atlas.

Ele fica escutando ativamente a fila new_messages por novas mensagens.

Ao receber uma mensagem, o corpo é decodificado de JSON.

Os campos status: "pending" e created_at são adicionados ao objeto da mensagem.

A mensagem enriquecida é inserida na coleção raw do banco de dados messages no MongoDB.

Em caso de falha no processamento (ex: erro de parse, falha no DB), a mensagem original é redirecionada para a fila failed_messages para análise posterior.

Um ack (acknowledgment) é enviado ao RabbitMQ para remover a mensagem da fila principal, garantindo que ela não seja processada novamente.