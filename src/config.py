import os
from dotenv import load_dotenv

load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
PATH_TO_WATCH = os.getenv("PATH_TO_WATCH")
CLIENT_SECRETS_FILE = os.getenv("CLIENT_SECRETS_FILE")
TOKEN_FILE = os.getenv("TOKEN_FILE")

# Permissões para Google Sheets e YouTube
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/youtube.upload'
]

if not all([SPREADSHEET_ID, PATH_TO_WATCH, CLIENT_SECRETS_FILE, TOKEN_FILE]):
    raise ValueError("variáveis de ambiente não estão no .env")