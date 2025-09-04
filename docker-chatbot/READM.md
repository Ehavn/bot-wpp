## 🤖 Microsserviço Consumidor de IA para WhatsApp
Este serviço é o segundo estágio em um pipeline de atendimento automatizado, atuando como o "cérebro" do sistema. Sua função é consumir mensagens já processadas e enriquecidas de uma fila, gerar respostas inteligentes usando IA, enviá-las ao usuário final via WhatsApp e persistir a conversa em um banco de dados.

## 📜 Descrição
Este projeto é um "worker" de longa duração que opera de forma reativa, baseado em eventos de uma fila do RabbitMQ. O fluxo de trabalho é o seguinte:

Escuta Ativa: O serviço se conecta a uma fila específica no RabbitMQ (ia_messages) e aguarda a chegada de "pacotes" de dados. Cada pacote contém a mensagem atual do usuário (já sanitizada) e o seu histórico de conversas.

Leitura de Contexto: Ao receber um pacote, o bot carrega o conteúdo de arquivos PDF locais. Esses documentos servem como uma base de conhecimento para a IA, garantindo respostas alinhadas à regras de negócio (ex: informações de produtos, apólices de seguro, etc.).

Geração da Resposta com IA: A pergunta do usuário, o histórico da conversa e o contexto extraído dos PDFs são enviados ao modelo gemini-1.5-flash do Google. A IA utiliza todas essas informações para gerar uma resposta coesa e contextual.

Envio via WhatsApp: A resposta gerada é enviada para o número de telefone do cliente através da API oficial do WhatsApp Business.

## Persistência da Conversa: Após o envio, a resposta da IA é salva no MongoDB, garantindo que o histórico da conversa esteja sempre completo e atualizado para futuras interações.

Este modelo garante que a lógica de IA esteja completamente desacoplada dos outros sistemas, permitindo que ela seja escalada e mantida de forma independente.

## ✨ Funcionalidades
Arquitetura Orientada a Eventos: Consome dados de uma fila do RabbitMQ, operando em tempo real e de forma assíncrona.

Integração com Google Gemini: Utiliza um modelo de IA generativa para criar respostas inteligentes.

Contexto a partir de PDFs: Enriquece o conhecimento da IA com documentos locais para fornecer respostas específicas e precisas.

Envio de Respostas Dinâmicas: Envia a resposta da IA para o número de telefone correto que originou a conversa.

## Persistência de Conversas: Salva as respostas geradas pela IA no MongoDB, criando um histórico completo do diálogo.

Pronto para Contêineres: Inclui um Dockerfile otimizado para build e deploy da aplicação.

## 🛠️ Tecnologias Utilizadas
Python 3.11

Pika: Para comunicação com o RabbitMQ.

Google Generative AI: Para a geração de respostas.

PDFPlumber: Para extração de texto de arquivos PDF.

Requests: Para interagir com a API do WhatsApp.

PyMongo: Para interagir com o MongoDB (via message_dao).

Docker: Para containerização.

## ⚙️ Configuração (✏️ ATUALIZADO)
As credenciais do projeto são gerenciadas pelo arquivo config/config.json.

API Key do Gemini: Obtenha sua chave de API no Google AI Studio.

WhatsApp Business: Preencha o token de acesso e o phone_number_id.

RabbitMQ: Configure o host, user, password e o nome da queue.

MongoDB: Adicione a connectionUri do seu cluster, o db_name e o collection_messages.

Pasta de PDFs: Certifique-se de que o caminho em pdfs_path existe.

Exemplo do config.json:

JSON

{
  "gemini": {
    "api_key": "SUA_API_KEY_DO_GEMINI"
  },
  "whatsapp": {
    "token": "SEU_TOKEN_DE_ACESSO_WHATSAPP",
    "phone_number_id": "ID_DO_SEU_NUMERO_DE_TELEFONE"
  },
  "rabbitmq": {
    "host": "localhost",
    "user": "admin",
    "password": "admin",
    "queue": "ia_messages"
  },
  "mongo": {
    "connectionUri": "mongodb+srv://<user>:<password>@<cluster-url>/<db-name>?retryWrites=true&w=majority",
    "db_name": "chatbot_db",
    "collection_messages": "messages"
  },
  "pdfs_path": "documents/pdfs"
}
## 🚀 Como Executar
Pré-requisitos:

Python 3.11 ou superior

Docker (para a opção com contêiner)

Aplicação "Preparador" em execução, publicando mensagens na fila ia_messages.

## ✨ Acesso a um cluster MongoDB com as credenciais corretas.

### 1. Execução Local
Bash

- 1. Clone o repositório e acesse a pasta da aplicação
- - ...

- 2. Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

- 3. Instale as dependências
pip install -r requirements.txt

- 4. Inicie o consumidor
- - (O nome do arquivo principal é app.py)
python app.py
O terminal exibirá a mensagem: Worker da IA iniciado. Aguardando mensagens na fila 'ia_messages'....

### 2. Execução com Docker
Bash

- 1. Na raiz do projeto, construa a imagem Docker
docker build -t consumidor-ia .

- 2. Execute o contêiner
- - A flag --network host permite que o container acesse serviços (como RabbitMQ e MongoDB)
- - que estão rodando no localhost da sua máquina.
docker run --name meu-consumidor-ia --network host -d consumidor-ia