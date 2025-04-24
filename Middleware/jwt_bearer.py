from fastapi.security import HTTPBearer
from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from Utils.jwt_manager import validate_token
from Utils.querys import Querys
from Config.db import get_db  # Importar la función para obtener la DB

class JWTBearer(HTTPBearer):
    def __init__(self):
        super().__init__()

    async def __call__(self, request: Request, db: Session = Depends(get_db)):  # Pasamos db aquí
        auth = await super().__call__(request)
        if not auth:
            raise HTTPException(status_code=403, detail="Credenciales no proporcionadas")
        
        data = validate_token(auth.credentials)
        cedula = int(data["cedula"])
        
        # Pasamos la sesión de la base de datos a Querys
        data_user = Querys(db).get_usuario_x_cedula(cedula)
        
        if not data_user or cedula != data_user:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
