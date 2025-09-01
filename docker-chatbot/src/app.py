# app_ai.py
import json
import threading
from src.services.gemini import GeminiConnector
from src.services.wpp import WhatsAppChat
from src.services.worker_ai import WorkerAI
from src.services.pdfManager import PDFManager

if __name__ == "__main__":
    with open("config/config.json", "r") as f:
        config = json.load(f)

    # Inicializa os serviços necessários
    pdfs_path = config.get("pdfs_path")
    pdf_manager = PDFManager(pdfs_path)
    gemini = GeminiConnector(config_file="config/config.json")
    whatsapp = WhatsAppChat(config_file="config/config.json", debug=True)

    # Inicializa o novo WorkerAI
    ai_worker = WorkerAI(
        gemini=gemini,
        whatsapp=whatsapp,
        pdf_manager=pdf_manager
    )

    # Inicia o worker
    # Não precisa mais de threading aqui, pois o start_consuming() já bloqueia
    try:
        ai_worker.run()
    except KeyboardInterrupt:
        print("\n🤖 Encerrando aplicação.")