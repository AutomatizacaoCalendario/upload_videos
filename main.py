import time
from watchdog.observers import Observer

from src import config
from src.auth import google_auth
from src.file_watcher.event_handler import VideoCreationHandler

if __name__ == "__main__":
    print("automação do calendário")
    
    try:
        services = google_auth.authenticate_google_services()
    except Exception as e:
        print(f"[ERROR] falha na inicialização: {e}")
        exit()

    if not all(services):
        print("[ERROR] erro autenticação dos serviços da Google, encerrando.")
        exit()
        
    # cria e inicia o handler para observar os arquivos
    event_handler = VideoCreationHandler(services)
    observer = Observer()
    observer.schedule(event_handler, config.PATH_TO_WATCH, recursive=False)
    
    print(f"[INFO] monitorando {config.PATH_TO_WATCH}, serviço rodando no background.")

    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] desligando o observador.")
        observer.stop()
    
    observer.join()
    print("[INFO] serviço encerrado.")