import os
from datetime import time
from dotenv import load_dotenv

load_dotenv() # Carga las variables desde el archivo .env

# Horario laboral
START_WORK_HOUR = time(7, 30)
END_WORK_HOUR = time(17, 30)
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
