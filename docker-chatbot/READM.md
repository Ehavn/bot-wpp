# Microsserviço Consumidor de IA para WhatsApp

Este serviço é o segundo estágio em um pipeline de atendimento automatizado, atuando como o "cérebro" do sistema. Sua função é consumir mensagens já processadas e enriquecidas de uma fila, gerar respostas inteligentes usando IA e enviá-las ao usuário final via WhatsApp.

## 📜 Descrição

Este projeto é um "worker" de longa duração que opera de forma reativa, baseado em eventos de uma fila do RabbitMQ. O fluxo de trabalho é o seguinte:

1.  **Escuta Ativa:** O serviço se conecta a uma fila específica no RabbitMQ (`ia_messages`) e aguarda a chegada de "pacotes" de dados. [cite_start]Cada pacote contém a mensagem atual do usuário (já sanitizada) e o seu histórico de conversas. 

2.  [cite_start]**Leitura de Contexto:** Ao receber um pacote, o bot carrega o conteúdo de arquivos PDF locais.  Esses documentos servem como uma base de conhecimento para a IA, garantindo respostas alinhadas à regras de negócio (ex: informações de produtos, apólices de seguro, etc.).

3.  **Geração da Resposta com IA:** A pergunta do usuário, o histórico da conversa e o contexto extraído dos PDFs são enviados ao modelo `gemini-1.5-flash` do Google. A IA utiliza todas essas informações para gerar uma resposta coesa e contextual.

4.  **Envio via WhatsApp:** A resposta gerada é enviada para o número de telefone do cliente através da API oficial do WhatsApp Business.

Este modelo garante que a lógica de IA esteja completamente desacoplada dos outros sistemas, permitindo que ela seja escalada e mantida de forma independente.

## ✨ Funcionalidades

* **Arquitetura Orientada a Eventos:** Consome dados de uma fila do RabbitMQ, operando em tempo real e de forma assíncrona.
* [cite_start]**Integração com Google Gemini:** Utiliza um modelo de IA generativa para criar respostas inteligentes. 
* [cite_start]**Contexto a partir de PDFs:** Enriquece o conhecimento da IA com documentos locais para fornecer respostas específicas e precisas. 
* **Envio de Respostas Dinâmicas:** Envia a resposta da IA para o número de telefone correto que originou a conversa.
* [cite_start]**Pronto para Contêineres:** Inclui um `Dockerfile` otimizado para build e deploy da aplicação. 

## 🛠️ Tecnologias Utilizadas

* [cite_start]**Python 3.11** 
* **Pika:** Para comunicação com o RabbitMQ.
* **Google Generative AI:** Para a geração de respostas.
* **PDFPlumber:** Para extração de texto de arquivos PDF.
* **Requests:** Para interagir com a API do WhatsApp.
* [cite_start]**Docker:** Para containerização. 

## ⚙️ Configuração

As credenciais do projeto são gerenciadas pelo arquivo `config/config.json`.

* **API Key do Gemini:** Obtenha sua chave de API no Google AI Studio.
* **WhatsApp Business:** Preencha o `token` de acesso e o `phone_number_id`.
* **RabbitMQ:** Configure o `host` e o nome da fila `queue_ia_messages`.
* **Pasta de PDFs:** Certifique-se de que o caminho em `pdfs_path` existe.

**Exemplo do `config.json`:**
```json
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
    "queue_ia_messages": "ia_messages"
  },
  "pdfs_path": "documentos/pdfs"
}
🚀 Como Executar
Pré-requisitos:

Python 3.11 ou superior 

Docker (para a opção com contêiner)

Aplicação 1 (Preparador) em execução, publicando mensagens na fila.

1. Execução Local
Bash

# 1. Clone o repositório e acesse a pasta desta aplicação
# ...

# 2. Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Inicie o consumidor
python app_ai.py
O terminal exibirá a mensagem: "Worker da IA iniciado. Aguardando mensagens na fila...".

2. Execução com Docker
Bash

# 1. Na raiz do projeto, construa a imagem Docker
docker build -t consumidor-ia .

# 2. Execute o contêiner
docker run --name meu-consumidor-ia --network host -d consumidor-ia