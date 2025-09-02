# Arquivo: src/app.py

from src.services.worker_preparer import WorkerPreparer
# O 'threading' não é mais necessário para um único worker

def main():
    """Função principal que inicia o worker."""
    # Inicializa o worker de preparação
    preparer_worker = WorkerPreparer()
    # Chama o método run() diretamente
    preparer_worker.run()

if __name__ == "__main__":
    main()