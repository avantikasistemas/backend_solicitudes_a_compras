from Config.db import BASE
from sqlalchemy import Column, BigInteger, Integer, DateTime
from datetime import datetime

class CiudadesFormacionDetalleModel(BASE):

    __tablename__= "ciudades_formacion_detalles"
    
    id = Column(BigInteger, primary_key=True)
    formacion_id = Column(BigInteger, nullable=False)
    ciudad_id = Column(BigInteger, nullable=False)
    estado = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)

    def __init__(self, data: dict):
        self.formacion_id = data['formacion_id']
        self.ciudad_id = data['ciudad_id']
        self.created_at = data['created_at']
