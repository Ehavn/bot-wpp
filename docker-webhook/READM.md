# Webhook para Enfileiramento de Mensagens
Este projeto é uma API de webhook construída com Flask. Sua principal função é receber requisições HTTP POST, extrair as mensagens de um payload JSON e publicá-las de forma assíncrona em uma fila do RabbitMQ para processamento posterior.

## 📜 Descrição
A aplicação atua como um ponto de entrada (endpoint) para webhooks, como os enviados por plataformas de mensagens (ex: WhatsApp Business API). Ela foi projetada para receber dados, validar a presença de mensagens no corpo da requisição e, em seguida, enfileirar cada mensagem individualmente no RabbitMQ. Isso garante que as mensagens recebidas não sejam perdidas e possam ser processadas por serviços consumidores de forma desacoplada e escalável.

## ✨ Funcionalidades
Endpoint HTTP: Expõe um endpoint (/) que aceita requisições do tipo POST.

Publicação em Fila: Conecta-se a um servidor RabbitMQ e publica mensagens em uma fila pré-configurada.

Mensagens Persistentes: As mensagens são publicadas no RabbitMQ com modo de entrega persistente, o que significa que elas serão salvas em disco e sobreviverão a reinicializações do broker.

Configuração Centralizada: As configurações do RabbitMQ e do servidor Flask são gerenciadas através do arquivo config/config.json.


Pronto para Contêineres: Inclui um Dockerfile para facilitar o build e o deploy da aplicação. 

## 🛠️ Tecnologias Utilizadas
Python 3.11


Flask: Micro-framework web para criar o endpoint do webhook. 


Pika: Biblioteca para comunicação com o RabbitMQ. 

Docker: Para containerização da aplicação.

## ⚙️ Configuração
Antes de executar o projeto, você precisa configurar as credenciais de acesso ao RabbitMQ e as configurações do servidor Flask.

Crie uma pasta chamada config.

Dentro de config/, crie o arquivo config.json com o seguinte conteúdo:

JSON

{
  "rabbitmq": {
    "host": "localhost",
    "user": "admin",
    "password": "admin",
    "queue": "incoming_messages"
  },
  "flask": {
    "port": 5000,
    "debug": true
  }
}
rabbitmq: Contém os dados de conexão com o servidor RabbitMQ.

flask: Define a porta e o modo de depuração do servidor Flask.

## 🚀 Como Executar
Você pode executar o projeto localmente com Python ou utilizando Docker.

Pré-requisitos
Python 3.11 ou superior

Docker (para a opção com contêiner)

Um servidor RabbitMQ em execução

### 1. Execução Local
Bash

- 1. Clone o repositório
git clone <url-do-seu-repositorio>
cd <nome-do-repositorio>

- 2. Crie e ative um ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

- 3. Instale as dependências
pip install -r requirements.txt

- 4. Inicie o servidor Flask
python main.py
O servidor estará em execução em http://localhost:5000.

### 2. Execução com Docker
Bash

- 1. Clone o repositório
git clone <url-do-seu-repositorio>
cd <nome-do-repositorio>

- 2. Construa a imagem Docker
docker build -t webhook-produtor .

- 3. Execute o contêiner, mapeando a porta
docker run --name meu-webhook -p 5000:5000 -d webhook-produtor

## 📝 Exemplo de Uso
Envie uma requisição POST para http://localhost:5000/ com um corpo JSON no seguinte formato:

JSON

{
  "value": {
    "messages": [
      {
        "from": "1234567890",
        "id": "wamid.ID",
        "text": {
          "body": "Olá, mundo!"
        },
        "timestamp": "1678886400",
        "type": "text"
      },
      {
        "from": "0987654321",
        "id": "wamid.ID2",
        "text": {
          "body": "Segunda mensagem"
        },
        "timestamp": "1678886401",
        "type": "text"
      }
    ]
  }
}
A API responderá com {"status": "ok"} e as duas mensagens serão publicadas na fila incoming_messages do RabbitMQ.