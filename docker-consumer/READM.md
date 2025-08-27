# Consumidor de Mensagens para MongoDB
Este serviço é um consumidor de mensagens projetado para escutar uma fila específica no RabbitMQ, receber mensagens e armazená-las como dados brutos em uma coleção no MongoDB Atlas.

## 📜 Descrição
O projeto atua como um worker que se conecta a um broker de mensageria (RabbitMQ) e a um banco de dados (MongoDB). Sua principal responsabilidade é garantir que as mensagens enviadas para a fila incoming_messages sejam persistidas de forma segura e confiável no banco de dados para processamento futuro ou arquivamento.

O serviço é configurado para ser resiliente, tentando se reconectar ao RabbitMQ caso o serviço não esteja disponível no momento da inicialização.

## ✨ Funcionalidades
Consumo de Mensagens: Conecta-se a uma fila RabbitMQ e consome mensagens de forma contínua.

Persistência de Dados: Salva cada mensagem recebida em uma coleção específica do MongoDB Atlas.

Configuração Centralizada: Gerencia as configurações de conexão do RabbitMQ e MongoDB através de um arquivo config.json.

Logging: Registra eventos importantes, como conexões estabelecidas, mensagens recebidas e erros, para facilitar o monitoramento e a depuração.

Pronto para Contêineres: Inclui um Dockerfile para fácil build e deploy da aplicação em ambientes containerizados.

## 🛠️ Tecnologias Utilizadas
Python 3.11

Pika: Biblioteca para comunicação com o RabbitMQ.

PyMongo: Biblioteca para comunicação com o MongoDB.

Docker: Para containerização da aplicação.

## ⚙️ Configuração
Antes de executar o projeto, você precisa configurar as credenciais de acesso ao RabbitMQ e ao MongoDB.

Navegue até a pasta config/.

Renomeie ou crie o arquivo config.json.

Preencha com suas informações:

JSON

{
  "rabbitmq": {
    "host": "localhost",
    "user": "seu_usuario_rabbitmq",
    "password": "sua_senha_rabbitmq",
    "queue": "incoming_messages"
  },
  "mongo": {
    "connectionUri": "sua_connection_string_mongodb_atlas",
    "db_name": "messages",
    "collection_raw": "raw"
  }
}
## 🚀 Como Executar
Você pode executar o projeto localmente com Python ou utilizando Docker.

Pré-requisitos
Python 3.11 ou superior

Docker (para a opção com contêiner)

Um servidor RabbitMQ em execução

Acesso a um cluster MongoDB Atlas

#### 1. Execução Local
Bash

- 1. Clone o repositório
git clone <url-do-seu-repositorio>
cd <nome-do-repositorio>

- 2. Crie e ative um ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

- 3. Instale as dependências
pip install -r requirements.txt

- 4. Inicie o consumidor
python main.py

#### 2. Execução com Docker
Bash

- 1. Clone o repositório
git clone <url-do-seu-repositorio>
cd <nome-do-repositorio>

- 2. Construa a imagem Docker
docker build -t consumidor-rabbitmq .

- 3. Execute o contêiner
docker run --name meu-consumidor -d consumidor-rabbitmq
Nota: Para o contêiner se conectar ao RabbitMQ rodando no localhost da sua máquina, talvez seja necessário ajustar a configuração de rede do Docker (ex: usando --network="host" ou alterando o host no config.json para host.docker.internal).

## 📁 Estrutura do Projeto
.
├── config/
│   └── config.json       # Arquivo de configuração
├── utils/
│   └── mongo_client.py   # Módulo para criar o cliente MongoDB
├── Dockerfile              # Define a imagem Docker da aplicação
├── logger.py               # Configuração do logger
├── main.py                 # Ponto de entrada da aplicação, inicia o consumidor
└── requirements.txt        # Lista de dependências Python
