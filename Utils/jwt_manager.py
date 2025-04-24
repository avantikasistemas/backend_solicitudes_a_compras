from fastapi import HTTPException
from jwt import encode, decode, ExpiredSignatureError
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv()

def create_token(data: dict):

    # Establece el tiempo de expiración (60 minutos desde el momento actual)
    expiration = datetime.now(timezone.utc) + timedelta(minutes=60)
    payload = {
        **data,
        "exp": expiration
    }
    token = encode(payload=payload, key=os.getenv("MY_SECRET_KEY"), algorithm="HS256")
    return token

def validate_token(token: str) -> dict:

    try:
        data: dict = decode(token, key=os.getenv("MY_SECRET_KEY"), algorithms=["HS256"])
        return data
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token ha expirado")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token inválido")
