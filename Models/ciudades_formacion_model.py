from Config.db import BASE
from sqlalchemy import Column, String, BigInteger, Integer, DateTime
from datetime import datetime

class CiudadesFormacionModel(BASE):

    __tablename__= "ciudades_formacion"
    
    id = Column(BigInteger, primary_key=True)
    nombre = Column(String, nullable=False)
    estado = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)
