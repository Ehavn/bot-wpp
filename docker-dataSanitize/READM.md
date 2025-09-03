## 📨 Microsserviço Preparador de Mensagens
Este serviço atua como o primeiro estágio em um pipeline de processamento de mensagens. Sua principal responsabilidade é consumir mensagens pendentes do MongoDB, enriquecê-las e prepará-las para o próximo estágio do processo, que envolve a interação com uma Inteligência Artificial.

## 📜 Descrição
O projeto opera em um fluxo contínuo e orientado a eventos:

Consumo: O serviço verifica continuamente o MongoDB em busca de mensagens com o status "pending".

Enriquecimento: Para cada mensagem encontrada, o serviço executa duas tarefas principais:

Busca de Histórico: Consulta o MongoDB para recuperar o histórico de conversas anteriores do mesmo remetente.

Sanitização: Mascara dados sensíveis no conteúdo da mensagem atual, como e-mails e CPFs, para proteger a privacidade.

Publicação: Por fim, ele empacota a mensagem atual sanitizada junto com o histórico e publica este pacote completo em uma segunda fila do RabbitMQ (ia_messages), de onde será consumido pela próxima aplicação do pipeline (Worker AI).

Atualização de Status: Após o processamento, a mensagem original no MongoDB é marcada como "processed" ou "failed".

Este design desacopla a recepção da mensagem do seu processamento final, garantindo um sistema mais resiliente, escalável e de fácil manutenção.

## 📂 Estrutura do Projeto
.
├── config/
│   └── config.json
├── src/
│   ├── dao/
│   │   └── message_dao.py
│   ├── services/
│   │   ├── sanitizer.py
│   │   ├── worker_ai.py
│   │   └── worker_preparer.py
│   ├── utils/
│   │   ├── logger.py
│   │   ├── mongo_client.py
│   │   └── rabbit_client.py
│   └── app.py
├── Dockerfile
├── requirements.txt
└── README.md
## 🛠️ Tecnologias Utilizadas
Python 3.11

Pika: Biblioteca para comunicação com o RabbitMQ.


PyMongo: Biblioteca para comunicação com o MongoDB. 

RabbitMQ: Broker de mensagens para o fluxo de eventos.

MongoDB: Banco de dados para armazenamento do histórico.


Docker: Para containerização da aplicação. 

## ⚙️ Configuração
Antes de executar, crie uma pasta config na raiz do projeto e, dentro dela, um arquivo config.json com a estrutura abaixo, substituindo os valores pelos da sua infraestrutura.

JSON

{
  "mongo": {
    "connectionUri": "mongodb+srv://user:pass@cluster.mongodb.net/your_db",
    "db_name": "messages",
    "collection_raw": "raw"
  },
  "rabbitmq": {
    "host": "localhost",
    "user": "admin",
    "password": "admin",
    "queue_new_messages": "new_messages",
    "queue_ia_messages": "ia_messages"
  }
}
## 🚀 Como Executar
- 1. Execução Local
Bash

- - Clone o repositório e navegue até a pasta
git clone <url-do-seu-repositorio>
cd <nome-do-repositorio>

- - Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

- - Instale as dependências
pip install -r requirements.txt

- - Inicie um servidor RabbitMQ (exemplo com Docker)
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management

- - Execute a aplicação
python src/app.py
- 2. Execução com Docker
Bash

- - Construa a imagem Docker a partir da raiz do projeto
docker build -t preparador-mensagens .

- - Execute o contêiner
- - (Certifique-se de que o RabbitMQ e o MongoDB estejam acessíveis)
- - Para conectar a serviços no localhost da sua máquina, use --network host
docker run --name meu-preparador --network host -d preparador-mensagens