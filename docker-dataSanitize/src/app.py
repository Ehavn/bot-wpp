# app.py
from src.services.worker_preparer import WorkerPreparer
import threading

def run_worker(worker):
    """Função para ser executada em uma thread."""
    worker_name = worker.__class__.__name__
    print(f"Iniciando {worker_name}...")
    try:
        worker.run()
    except KeyboardInterrupt:
        print(f"{worker_name} interrompido.")

def main():
    # Inicializa apenas o worker de preparação
    preparer_worker = WorkerPreparer()

    # Cria a thread para o worker
    preparer_thread = threading.Thread(target=run_worker, args=(preparer_worker,))

    # Inicia a thread
    preparer_thread.start()
    print("Aplicação 1 (Preparador) em execução. Pressione CTRL+C para sair.")
    
    preparer_thread.join()

if __name__ == "__main__":
    main()