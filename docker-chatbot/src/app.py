# app.py
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env (para desenvolvimento)
load_dotenv()

from src.services.gemini import GeminiConnector
from src.services.wpp import WhatsAppChat
from src.services.worker_ai import WorkerAI
from src.services.pdfManager import PDFManager
from src.utils.mongo_client import get_mongo_client
from src.dao.message_dao import MessageDAO
from src.utils.logger import get_logger

logger = get_logger("ApplicationRunner")

if __name__ == "__main__":
    logger.info("🚀 Iniciando a aplicação...")

    # --- 1. INICIALIZAÇÃO DO MONGO E DAO ---
    try:
        mongo_client, mongo_config = get_mongo_client()
        message_dao = MessageDAO(db_client=mongo_client, config=mongo_config)
        logger.info("✅ Conexão com o MongoDB estabelecida com sucesso.")
    except Exception as e:
        logger.critical(f"❌ Falha crítica ao conectar com o MongoDB: {e}", exc_info=True)
        exit(1) # Encerra se não conseguir conectar ao banco

    # --- 2. INICIALIZAÇÃO DOS SERVIÇOS ---
    try:
        # Pega o caminho dos PDFs a partir das variáveis de ambiente
        pdfs_path = os.getenv("PDFS_PATH", "documents/pdfs")
        
        pdf_manager = PDFManager(pdfs_path)
        gemini = GeminiConnector()
        whatsapp = WhatsAppChat(debug=True)
        logger.info("✅ Todos os serviços foram inicializados com sucesso.")
    except Exception as e:
        logger.critical(f"❌ Falha ao inicializar os serviços: {e}", exc_info=True)
        exit(1)

    # --- 3. INJEÇÃO DE DEPENDÊNCIAS E EXECUÇÃO DO WORKER ---
    ai_worker = WorkerAI(
        gemini=gemini,
        whatsapp=whatsapp,
        pdf_manager=pdf_manager,
        message_dao=message_dao
    )

    try:
        logger.info("🤖 Worker da IA pronto para iniciar o consumo de mensagens.")
        ai_worker.run()
    except KeyboardInterrupt:
        logger.info("\n🛑 Aplicação encerrada pelo usuário.")
    except Exception as e:
        logger.critical(f"❌ Erro fatal no worker da IA: {e}", exc_info=True)
        exit(1)