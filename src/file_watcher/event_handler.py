import os
import time
import logging
from datetime import datetime
from watchdog.events import FileSystemEventHandler
from tkinter import simpledialog, Tk

from src.services import youtube_service, sheets_service

class VideoCreationHandler(FileSystemEventHandler):
    def __init__(self, services):
        self.service_sheets, self.service_youtube = services

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = event.src_path
        filename = os.path.basename(file_path)
        
        if not filename.lower().endswith(('.mkv', '.mp4', '.mov', '.flv')):
            return

        logging.info(f"\n[EVENT] arquivo de vídeo detectado: {filename}")

        # esperar o obs terminar de gravar antes de escrever o arquivo
        try:
            file_size = -1
            while file_size != os.path.getsize(file_path):
                file_size = os.path.getsize(file_path)
                time.sleep(10) # espera 10 segundos para ver se o tamanho do arquivo muda
            logging.info("[INFO] arquivo estabilizado.")
        except FileNotFoundError:
            logging.warning("[WARNING] gravação em andamento ou arquivo não encontrado, ignorando.")
            return

        try:
            # extrai data do nome do arquivo
            date_str = filename.split(' ')[0]
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            
            # pergunta nome da aula
            root = Tk()
            root.withdraw()
            class_name = simpledialog.askstring("Nome da Aula", "Insira nome:")
            root.destroy()
            
            if not class_name:
                logging.warning("[WARNING] nenhum nome de aula, abortando.")
                return
            
            # faz upload
            description = f"Aula de {class_name} / {date_obj.strftime('%d/%m/%Y')}"
            video_link = youtube_service.upload_video(self.service_youtube, file_path, class_name, description)

            # atualiza a planilha
            if video_link:
                sheets_service.update_calendar_entry(self.service_sheets, date_obj, video_link, class_name)

        except (ValueError, IndexError):
            logging.error(f"[ERROR] '{filename}' não está no formato esperado, ignorando.")
        except Exception as e:
            logging.error(f"[ERROR] erro inesperado: {e}")