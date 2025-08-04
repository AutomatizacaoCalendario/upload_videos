import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src import config

def authenticate_google_services():
    """
    Autentica com a conta do Google usando OAuth2.
    """
    creds = None
    
    # token.json existe? puxa credenciais
    if os.path.exists(config.TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(config.TOKEN_FILE, config.SCOPES)

    # credenciais expiradas? sem arquivo token.json? abre janela da google para logar
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(config.CLIENT_SECRETS_FILE, config.SCOPES)
            creds = flow.run_local_server(port=0)

        # salva as credenciais em token.json
        with open(config.TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    try:
        service_sheets = build('sheets', 'v4', credentials=creds)
        service_youtube = build('youtube', 'v3', credentials=creds)
        print("Autenticação success.")
        return service_sheets, service_youtube
    except HttpError as err:
        print(f"Autenticação error: {err}")
        return None, None