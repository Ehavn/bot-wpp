# Pipeline de Sanitização e Transferência de Mensagens
Este serviço implementa um pipeline de processamento de dados que opera em duas fases principais: sanitização e transferência. Ele foi projetado para ler mensagens de uma coleção no MongoDB, mascarar dados sensíveis como CPFs, e-mails e telefones, e, em seguida, mover os dados limpos para uma coleção separada, pronta para consumo seguro.

## 📜 Descrição
O projeto funciona como um processo ETL (Extração, Transformação, Carga) em lote. Ele é composto por dois "workers" que executam em sequência:

Worker de Sanitização (WorkerSanitize): Busca por mensagens com status "pending" na coleção de dados brutos (raw). Para cada mensagem, ele aplica uma série de regras de sanitização para mascarar informações pessoais identificáveis (PII). Após o processo, o status da mensagem é atualizado para "sanitized".

Worker de Transferência (WorkerTransfer): Busca por mensagens que já foram sanitizadas (status "sanitized"). Ele copia essas mensagens para uma nova coleção (sanitize) e, por fim, atualiza o status da mensagem original para "transferred", completando o ciclo.

Este processo garante que os dados sensíveis sejam protegidos antes de serem expostos a outros sistemas ou processos, como bots de atendimento ou plataformas de análise.

## ✨ Funcionalidades
Processamento em Lote: Projetado para processar múltiplas mensagens em cada execução.

Mascaramento de Dados: Identifica e mascara automaticamente CPFs, e-mails e números de telefone no conteúdo das mensagens.

Pipeline de Múltiplos Estágios: Separa as responsabilidades de sanitização e transferência em workers distintos.

Controle de Estado: Utiliza um campo status ("pending", "sanitized", "transferred") para controlar o progresso de cada mensagem no pipeline.

Acesso a Dados Organizado: Utiliza uma classe DAO (MessageDAO) para abstrair e centralizar todas as operações com o MongoDB.


Pronto para Contêineres: Inclui um Dockerfile para fácil empacotamento e execução em ambientes containerizados. 

## 🛠️ Tecnologias Utilizadas
Python 3.11


PyMongo: Biblioteca para comunicação com o MongoDB. 

Docker: Para containerização da aplicação.

## ⚙️ Configuração
Antes de executar, é necessário configurar a conexão com o MongoDB.

Crie uma pasta chamada config.

Dentro de config/, crie o arquivo config.json com a estrutura abaixo, substituindo connectionUri pela sua string de conexão do MongoDB Atlas.

JSON

{
  "mongodb": {
    "connectionUri": "sua_connection_string_do_mongodb",
    "db_name": "messages",
    "collection_raw": "raw",
    "collection_sanitize": "sanitize"
  }
}
## 🚀 Como Executar
Você pode executar o projeto localmente com Python ou utilizando Docker.

Pré-requisitos
Python 3.11 ou superior

Docker (para a opção com contêiner)

Acesso a um cluster MongoDB com as coleções e dados necessários.

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

- 4. Execute o pipeline
python main.py
### 2. Execução com Docker
Bash

- 1. Clone o repositório
git clone <url-do-seu-repositorio>
cd <nome-do-repositorio>

- 2. Construa a imagem Docker
docker build -t worker-pipeline .

- 3. Execute o contêiner
docker run --name meu-worker -d worker-pipeline

Ao ser executado, o main.py irá instanciar e rodar o worker de sanitização e, logo em seguida, o worker de transferência, processando todas as mensagens pendentes.