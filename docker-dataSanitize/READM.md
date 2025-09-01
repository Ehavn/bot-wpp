# Microsserviço Preparador de Mensagens

Este serviço atua como o primeiro estágio em um pipeline de processamento de mensagens. Sua principal responsabilidade é consumir mensagens de uma fila, enriquecê-las e prepará-las para o próximo estágio do processo, que envolve a interação com uma Inteligência Artificial.

## 📜 Descrição

O projeto opera em um fluxo contínuo e orientado a eventos:

1.  **Consumo:** O serviço escuta uma fila no RabbitMQ (`new_messages`), aguardando a chegada de novas mensagens (enviadas por um webhook, por exemplo).
2.  **Enriquecimento:** Para cada mensagem recebida, o serviço executa duas tarefas principais:
    * **Sanitização:** Mascara dados sensíveis no conteúdo da mensagem, como e-mails e CPFs, para proteger a privacidade.
    * **Busca de Histórico:** Consulta um banco de dados MongoDB para recuperar o histórico de conversas anteriores do mesmo remetente.
3.  **Publicação:** Por fim, ele empacota a *mensagem atual sanitizada* junto com o *histórico* e publica este pacote completo em uma segunda fila do RabbitMQ (`ia_messages`), de onde será consumido pela próxima aplicação do pipeline.

Este design desacopla a recepção da mensagem do seu processamento final, garantindo um sistema mais resiliente, escalável e de fácil manutenção.

## ✨ Funcionalidades

* **Processamento em Tempo Real:** Opera como um serviço de longa duração que processa mensagens assim que elas chegam.
* **Arquitetura Orientada a Eventos:** Utiliza RabbitMQ para comunicação assíncrona entre os componentes do sistema.
* **Mascaramento de Dados:** Protege informações pessoais identificáveis (PII) antes de enviá-las para os próximos estágios.
* **Enriquecimento de Dados:** Agrega contexto histórico às novas mensagens, fornecendo mais informações para a IA.
* **Persistência de Histórico:** Utiliza o MongoDB para armazenar um log completo e imutável de todas as mensagens recebidas.
* [cite_start]**Pronto para Contêineres:** Inclui um `Dockerfile` para fácil empacotamento e execução em ambientes containerizados. [cite: 2, 3]

## 🛠️ Tecnologias Utilizadas

* **Python 3.11**
* **Pika:** Biblioteca para comunicação com o RabbitMQ.
* [cite_start]**PyMongo:** Biblioteca para comunicação com o MongoDB. [cite: 1]
* **RabbitMQ:** Broker de mensagens para o fluxo de eventos.
* **MongoDB:** Banco de dados para armazenamento do histórico.
* [cite_start]**Docker:** Para containerização da aplicação. [cite: 2, 3]

## ⚙️ Configuração

Antes de executar, é necessário configurar as conexões com o MongoDB e o RabbitMQ.

1.  Crie uma pasta chamada `config`.
2.  Dentro de `config/`, crie o arquivo `config.json` com a estrutura abaixo, substituindo os valores pelos da sua infraestrutura.

```json
{
  "mongodb": {
    "connectionUri": "sua_connection_string_do_mongodb",
    "db_name": "messages",
    "collection_raw": "raw"
  },
  "rabbitmq": {
    "host": "localhost",
    "queue_new_messages": "new_messages",
    "queue_ia_messages": "ia_messages"
  }
}
🚀 Como Executar
Você pode executar o projeto localmente com Python ou utilizando Docker.

Pré-requisitos:

Python 3.11 ou superior

Docker e Docker Compose (recomendado para rodar o RabbitMQ)

Acesso a um cluster MongoDB.

1. Execução Local
Bash

# 1. Clone o repositório
git clone <url-do-seu-repositorio>
cd <nome-do-repositorio>

# 2. Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Inicie um servidor RabbitMQ (exemplo com Docker)
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management

# 5. Execute a aplicação
python app.py
2. Execução com Docker
Bash

# 1. Clone o repositório
git clone <url-do-seu-repositorio>
cd <nome-do-repositorio>

# 2. Construa a imagem Docker
docker build -t preparador-mensagens .

# 3. Execute o contêiner
# (Certifique-se de que o RabbitMQ e o MongoDB estejam acessíveis pela rede)
docker run --name meu-preparador --network host -d preparador-mensagens