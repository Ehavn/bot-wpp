from services.gemini import GeminiConnector
from services.wpp import WhatsAppChat
from services.worker_fetch_sanitized import WorkerFetchSanitized
from services.pdfManager import PDFManager
import threading
import json

if __name__ == "__main__":
    with open("config/config.json", "r") as f:
        config = json.load(f)

    # Inicializa PDFManager com pasta de PDFs do config
    pdfs_path = config.get("pdfs_path")
    pdf_manager = PDFManager(pdfs_path)

    # Cria instâncias do GeminiConnector e WhatsApp
    gemini = GeminiConnector(config_file="config/config.json")
    whatsapp = WhatsAppChat(debug=True)

    # Inicializa WorkerFetchSanitized em thread separada
    # Passa pdf_manager para o worker, assim ele pode usar trechos dos PDFs como contexto
    fetcher = WorkerFetchSanitized(
        gemini=gemini,
        whatsapp=whatsapp,
        pdf_manager=pdf_manager,  # <- adiciona aqui
        poll_interval=5
    )
    threading.Thread(target=fetcher.run_loop, daemon=True).start()

    print("🤖 Worker iniciado. Aguardando mensagens sanitizadas no Mongo...")

    # Mantém o programa rodando para threads daemon
    try:
        while True:
            pass  # Mantém main alive
    except KeyboardInterrupt:
        print("\n🤖 Encerrando aplicação.")
        fetcher.running = False
