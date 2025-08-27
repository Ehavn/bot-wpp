# Chatbot com IA para Atendimento via WhatsApp
Este serviço é um chatbot inteligente projetado para automatizar o atendimento ao cliente via WhatsApp. Ele busca mensagens de uma base de dados, utiliza o poder da IA generativa do Google Gemini para formular respostas contextuais e as envia de volta ao usuário através da API do WhatsApp.

## 📜 Descrição
O projeto funciona como um "worker" contínuo que monitora uma coleção no MongoDB em busca de novas mensagens de clientes (previamente sanitizadas por outro serviço). Ao encontrar uma nova mensagem, o chatbot executa o seguinte fluxo:

Leitura do Contexto: O bot carrega o conteúdo de arquivos PDF localizados em uma pasta específica. Esses documentos servem como base de conhecimento, permitindo que a IA forneça respostas precisas e alinhadas ao negócio (ex: apólices de seguro, manuais de produtos, etc.).

Geração da Resposta com IA: A mensagem do usuário, juntamente com as diretrizes de comportamento e o contexto extraído dos PDFs, é enviada para o modelo gemini-1.5-flash do Google. A IA gera uma resposta humanizada e útil.

Envio via WhatsApp: A resposta gerada pela IA é enviada para o número de telefone do cliente através da API oficial do WhatsApp Business.

Atualização de Status: Após o envio, a mensagem no banco de dados é marcada como "lida" (read) para evitar reprocessamento.

Este ciclo se repete continuamente, garantindo que as mensagens sejam processadas em tempo real.

## ✨ Funcionalidades
Integração com Google Gemini: Utiliza um modelo de IA generativa para criar respostas inteligentes e contextuais.

Sistema de Diretrizes (Prompt Engineering): Configura o comportamento do chatbot com diretrizes iniciais claras (ex: "Você é um assistente de seguros", "Seja educado e direto").

Contexto a partir de PDFs: Enriquece o conhecimento da IA carregando o conteúdo de documentos PDF, permitindo respostas baseadas em informações específicas.

Integração com WhatsApp Business API: Envia as respostas diretamente para o WhatsApp do usuário final.

Processamento Assíncrono: Roda em um loop contínuo (thread) para monitorar e processar novas mensagens sem interrupção.

Organização e Configuração: Gerencia todas as chaves de API, credenciais e parâmetros através de um único arquivo config.json.

Pronto para Contêineres: Inclui um Dockerfile para fácil build e deploy da aplicação em ambientes isolados.

## 🛠️ Tecnologias Utilizadas
Python 3.11

Google Generative AI (gemini-1.5-flash): Para a geração de respostas.

PyMongo: Para comunicação com o banco de dados MongoDB.

PDFPlumber: Para extração de texto de arquivos PDF.

Requests: Para interagir com a API do WhatsApp.

Docker: Para containerização.

## ⚙️ Configuração
Antes de executar o projeto, você precisa configurar todas as credenciais no arquivo config/config.json.

API Key do Gemini: Obtenha sua chave de API no Google AI Studio e adicione-a à seção gemini.

MongoDB: Insira sua string de conexão do MongoDB Atlas na seção mongo.

WhatsApp Business: Preencha o token de acesso, o ID do número de telefone e o número de destino na seção whatsapp.

Pasta de PDFs: Certifique-se de que o caminho em pdfs_path existe e contém os arquivos PDF que você deseja usar como contexto.

Exemplo do config.json:

JSON

{
  "gemini": {
    "api_key": "SUA_API_KEY_DO_GEMINI"
  },
  "mongo": {
    "connectionUri": "SUA_CONNECTION_STRING_DO_MONGODB",
    "db_name": "messages",
    "collection_sanitize": "sanitize"
  },
  "whatsapp": {
    "token": "SEU_TOKEN_DE_ACESSO_WHATSAPP",
    "phone_number_id": "ID_DO_SEU_NUMERO_DE_TELEFONE",
    "to_phone_number": "NUMERO_DO_CLIENTE_PARA_TESTES"
  },
  "pdfs_path": "documentos/pdfs"
}
## 🚀 Como Executar
Você pode executar o projeto localmente com Python ou utilizando Docker.

Pré-requisitos
Python 3.11 ou superior

Docker (para a opção com contêiner)

Conta no Google AI Studio, MongoDB Atlas e Meta for Developers (WhatsApp API).

Arquivos PDF na pasta configurada.

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

- 4. Inicie o bot
python main.py
O terminal exibirá a mensagem "🤖 Worker iniciado. Aguardando mensagens sanitizadas no Mongo...".

### 2. Execução com Docker
Bash

- 1. Clone o repositório
git clone <url-do-seu-repositorio>
cd <nome-do-repositorio>

- 2. Construa a imagem Docker
- - O Dockerfile já copia a pasta de documentos, certifique-se que ela está presente.
docker build -t chatbot-whatsapp .

- 3. Execute o contêiner
docker run --name meu-chatbot -d chatbot-whatsapp