## 🚧 Serviço de Captura de Erros (Dead Letter Queue)
Este serviço implementa um padrão de Dead Letter Queue, atuando como um "coletor" de segurança para mensagens que falharam durante o processamento em outras partes do sistema. Sua única responsabilidade é capturar, registrar e armazenar essas falhas para garantir que nenhum dado seja perdido, permitindo análise e recuperação futura.

## ✨ Funcionalidades

Consumidor Dedicado: Roda como um serviço contínuo que escuta ativamente uma fila de erros específica no RabbitMQ (failed_messages).




Armazenamento Seguro: Ao receber uma mensagem da fila de erros, ele a persiste em uma coleção dedicada no MongoDB (dead_letter_messages).



Enriquecimento de Dados: Adiciona informações cruciais para auditoria, como a data e hora em que a falha foi registrada (failed_at) e um status inicial de "unresolved".


## 📂 Estrutura do Projeto
.
├── src/
│   ├── consumers/
│   │   └── error_consumer.py     # Lógica do consumidor da fila de erros
│   ├── logic/
│   │   ├── db_logic.py           # Funções para interagir com o MongoDB
│   │   └── retry_logic.py        # Lógica para reenfileirar mensagens
│   └── utils/
│       ├── logger.py             # Configuração de logs
│       ├── mongo_client.py       # Conexão com MongoDB
│       └── rabbit_client.py      # Conexão com RabbitMQ
├── app_error_handler.py          # Entrypoint para o consumidor de erros
├── config.json                   # Arquivo de configuração
├── requirements.txt
└── Dockerfile
## ⚙️ Configuração (config.json)
O projeto utiliza um arquivo config.json para gerenciar as conexões.

JSON

{
  "rabbitmq": {
    "host": "localhost",
    "user": "admin",
    "password": "admin",
    "queue_main": "new_messages",
    "queue_error": "failed_messages"
  },
  "mongo": {
    "connectionUri": "mongodb+srv://user:pass@cluster.mongodb.net/db_name",
    "db_name": "messages",
    "collection_dead_letter": "dead_letter_messages"
  }
}
## 🚀 Como Executar com Docker
Este serviço foi projetado para rodar continuamente em background.

Bash

- 1. Na raiz do projeto, construa a imagem do serviço
docker build -t error-handler-service .

- 2. Execute o contêiner em modo detached (-d)
- - Use --network="host" para conectar-se a serviços (RabbitMQ, Mongo) no seu localhost
docker run -d --name error-handler --network="host" error-handler-service
Após a execução, o serviço estará escutando a fila 

failed_messages e salvando qualquer mensagem que chegue nela diretamente no MongoDB, na coleção dead_letter_messages.