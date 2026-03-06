import os
from datetime import time
from dotenv import load_dotenv

load_dotenv() # Carga las variables desde el archivo .env

# Horario laboral
START_WORK_HOUR = time(7, 30)
END_WORK_HOUR = time(17, 30)

# Microsoft Graph
MICROSOFT_CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID")
MICROSOFT_CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET")
MICROSOFT_TENANT_ID = os.getenv("MICROSOFT_TENANT_ID")
MICROSOFT_URL = os.getenv("MICROSOFT_URL")
SMTP_EMAIL_SEND = os.getenv("SMTP_EMAIL_SEND")
