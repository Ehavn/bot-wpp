# app.py
import json
from src.services.gemini import GeminiConnector
from src.services.wpp import WhatsAppChat
from src.services.worker_ai import WorkerAI
from src.services.pdfManager import PDFManager
from src.utils.mongo_client import get_mongo_client # <-- 1. Importações
from src.services.message_dao import MessageDAO

if __name__ == "__main__":
    with open("config/config.json", "r") as f:
        config = json.load(f)

    # --- 2. INICIALIZAÇÃO DO MONGO E DAO ---
    try:
        mongo_client, mongo_config = get_mongo_client(config_file="config/config.json")
        message_dao = MessageDAO(db_client=mongo_client, config=mongo_config)
        print("✅ Conexão com MongoDB estabelecida.")
    except Exception as e:
        print(f"❌ Falha ao conectar com o MongoDB: {e}")
        exit() # Encerra se não conseguir conectar ao banco

    # Inicializa os outros serviços
    pdfs_path = config.get("pdfs_path")
    pdf_manager = PDFManager(pdfs_path)
    gemini = GeminiConnector(config_file="config/config.json")
    whatsapp = WhatsAppChat(config_file="config/config.json", debug=True)

    # --- 3. INJETA O DAO NO WORKER ---
    ai_worker = WorkerAI(
        gemini=gemini,
        whatsapp=whatsapp,
        pdf_manager=pdf_manager,
        message_dao=message_dao # <-- Passando o DAO
    )

    try:
        ai_worker.run()
    except KeyboardInterrupt:
        print("\n🤖 Encerrando aplicação.")