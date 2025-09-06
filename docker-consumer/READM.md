## 📥 Docker Consumer - RabbitMQ to MongoDB
Este serviço atua como um consumidor, responsável por processar mensagens de uma fila RabbitMQ e armazená-las de forma segura em um banco de dados MongoDB Atlas. Cada mensagem recebida é enriquecida com um status inicial "pending" antes de ser persistida.

## 📂 Estrutura do Projeto
.
├── config/
│   └── config.json         # Configurações NÃO-SENSÍVEIS da aplicação
├── src/
│   ├── app.py              # Entrypoint principal que inicia o consumidor
│   ├── consumer/
│   │   └── rabbitmq_consumer.py # Lógica de consumo e inserção no MongoDB
│   └── utils/
│       ├── mongo_client.py     # Lógica de conexão com MongoDB
│       └── logger.py           # Configuração de logs
├── .env                    # Arquivo para armazenar segredos (NÃO versionado)
├── requirements.txt        # Dependências Python
├── Dockerfile              # Configuração de build do container
└── README.md

## ⚙️ Configuração
A configuração do projeto é dividida em dois arquivos para máxima segurança:

1.  `config/config.json`: Armazena configurações **não-sensíveis**, como nomes de filas e bancos de dados. Este arquivo pode ser versionado no Git.
2.  `.env`: Armazena **segredos** (senhas, chaves de API, URIs de conexão). **Este arquivo nunca deve ser enviado para o Git** e precisa ser criado manualmente em cada ambiente.

**Exemplo do arquivo `.env`:**
```ini
# Configurações do RabbitMQ
RABBIT_HOST=localhost
RABBIT_USER=admin
RABBIT_PASS=admin

# Configuração do Mongo
MONGO_CONNECTION_URI="mongodb+srv://usuario:senha@cluster.mongodb.net/..."
▶️ Executando Localmente
Criar e ativar o ambiente virtual
Bash

python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate      # Windows
Instalar pacotes
Bash

pip install -r requirements.txt
Iniciar o consumidor
Bash

python src/app.py
🐳 Executando com Docker
Build da imagem Docker:

Bash

docker build -t rabbitmq-consumer .
Rodar o container:
Para rodar o container, você precisa passar as variáveis de ambiente do seu arquivo .env.

Bash

docker run --rm --name consumer-instance \
  --env-file .env \
  rabbitmq-consumer
📝 Logs
Os logs são enviados para a saída padrão (stdout) em formato JSON estruturado, ideal para integração com plataformas de monitoramento como Datadog, Splunk ou a stack ELK.

Exemplo de saída:

JSON

{"asctime": "2025-09-05 19:15:00,123", "name": "app", "levelname": "INFO", "message": "iniciando consumidor..."}
{"asctime": "2025-09-05 19:15:01,456", "name": "src.utils.mongo_client", "levelname": "INFO", "message": "conexao com mongodb estabelecida com sucesso"}
{"asctime": "2025-09-05 19:15:02,789", "name": "src.consumer.rabbitmq_consumer", "levelname": "INFO", "message": "consumidor iniciado, aguardando mensagens..."}
{"asctime": "2025-09-05 19:15:10,321", "name": "src.consumer.rabbitmq_consumer", "levelname": "INFO", "message": "mensagem recebida", "body_snippet": "b'{\"id\": \"msg1\"}'"}
{"asctime": "2025-09-05 19:15:10,325", "name": "src.consumer.rabbitmq_consumer", "levelname": "INFO", "message": "documento inserido no mongodb", "inserted_id": "68e8e2c8a7b3f9b2f3e1a1b8"}
📌 Fluxo de Processamento
O consumidor estabelece conexões com o RabbitMQ e o MongoDB.

Ele fica escutando ativamente a fila new_messages.

Ao receber uma mensagem, o corpo é decodificado e enriquecido.

A mensagem enriquecida é inserida na coleção raw do MongoDB.

Em caso de falha no processamento, a mensagem é redirecionada para a fila failed_messages para análise posterior.

Um ack (acknowledgment) é enviado ao RabbitMQ para remover a mensagem da fila principal.


---

### 2. `Dockerfile` (Versão Final)
A única mudança aqui é a adição de `exec` ao `CMD` para garantir um encerramento mais limpo do container.

```dockerfile
# Dockerfile Otimizado com Múltiplos Estágios

# ---- Estágio 1: Build ----
# Usamos uma imagem completa para instalar as dependências, que pode ser descartada depois.
FROM python:3.11 as builder

WORKDIR /usr/src/app

# Instala as dependências de forma segura em um ambiente virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copia e instala as dependências
COPY requirements.txt .
# Instala dependências de build, instala pacotes Python, e depois remove as de build
RUN apt-get update && apt-get install -y --no-install-recommends gcc libssl-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y gcc libssl-dev && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# ---- Estágio 2: Final ----
# Usamos uma imagem 'slim' que é muito menor para a versão final.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED True
WORKDIR /app

# Cria um usuário não-root para segurança
RUN useradd --create-home appuser
USER appuser

# Copia o ambiente virtual com as dependências do estágio de build
COPY --from=builder /opt/venv /opt/venv

# Copia o código da aplicação e o config não-sensível
COPY config/ ./config/
COPY src/ ./src/

# Define o caminho para usar os pacotes do ambiente virtual e executa a aplicação
ENV PATH="/opt/venv/bin:$PATH"
CMD ["exec", "python", "src/app.py"]