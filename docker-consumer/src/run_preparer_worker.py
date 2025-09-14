# Arquivo: src/run_preparer_worker.py

from src.services.worker_preparer import WorkerPreparer
from src.utils.logger import get_logger

def main():
    """Função principal que inicia o worker de preparação."""
    logger = get_logger("Preparer_Worker_Runner")
    logger.info("Iniciando o Worker de Preparação...")
    try:
        preparer_worker = WorkerPreparer()
        preparer_worker.run()
    except Exception as e:
        logger.critical(f"Erro fatal ao iniciar o Worker de Preparação: {e}", exc_info=True)

if __name__ == "__main__":
    main()