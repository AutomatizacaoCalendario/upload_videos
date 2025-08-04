import time
import logging
from watchdog.observers import Observer

from src import config
from src.auth import google_auth
from src.file_watcher.event_handler import VideoCreationHandler

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='automacao_upload_videos.log',
        filemode='a'
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logging.getLogger().addHandler(console_handler)

    logging.info("iniciando")
    
    try:
        services = google_auth.authenticate_google_services()
    except Exception as e:
        logging.error(f"[ERROR] falha na inicialização: {e}")
        exit()

    if not all(services):
        logging.error("[ERROR] erro autenticação dos serviços da Google, encerrando.")
        exit()
        
    # cria e inicia o handler para observar os arquivos
    event_handler = VideoCreationHandler(services)
    observer = Observer()
    observer.schedule(event_handler, config.PATH_TO_WATCH, recursive=False)
    
    logging.info(f"[INFO] monitorando {config.PATH_TO_WATCH}, serviço rodando no background.")

    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("\n[INFO] desligando o observador.")
        observer.stop()
    
    observer.join()
    logging.info("[INFO] serviço encerrado.")