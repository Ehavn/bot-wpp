from src.services.worker_sanitize import WorkerSanitize
from src.services.worker_transfer import WorkerTransfer

def main():
    # Inicializa os workers
    sanitizer_worker = WorkerSanitize()
    transfer_worker = WorkerTransfer()

    # Executa os workers
    sanitizer_worker.run()
    transfer_worker.run()

if __name__ == "__main__":
    main()