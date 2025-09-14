# Arquivo: src/run_ai_worker.py

from src.services.worker_ai import WorkerAI 
from src.utils.logger import get_logger

def main():
    """Função principal que inicia o worker de IA."""
    logger = get_logger("AI_Worker_Runner")
    logger.info("Iniciando o Worker de IA...")
    try:
        # Agora o Python sabe o que é WorkerAI por causa da importação
        ai_worker = WorkerAI()
        ai_worker.run()
    except Exception as e:
        logger.critical(f"Erro fatal ao iniciar o Worker de IA: {e}", exc_info=True)

if __name__ == "__main__":
    main()