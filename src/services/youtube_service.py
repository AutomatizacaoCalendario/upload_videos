from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import logging


def upload_video(service_youtube, file_path, title, description):
    """
    Faz o upload de vídeo como 'não listado'.
    Returns: URL do vídeo | None.
    """
    try:
        logging.debug(f"Iniciando upload: '{title}'")
        request_body = {
            'snippet': {
                'title': title,
                'description': description
            },
            'status': {
                'privacyStatus': 'unlisted',
                'selfDeclaredMadeForKids': False
            }
        }

        media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
        
        response_upload = service_youtube.videos().insert(
            part='snippet,status',
            body=request_body,
            media_body=media
        ).execute()

        video_id = response_upload.get('id')
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        logging.info(f"Upload success.")
        return video_url
        
    except HttpError as err:
        logging.error(f"Upload error: {err}")
        return None
    