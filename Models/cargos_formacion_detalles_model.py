from Config.db import BASE
from sqlalchemy import Column, BigInteger, Integer, DateTime
from datetime import datetime

class CargosFormacionDetalleModel(BASE):

    __tablename__= "cargos_formacion_detalles"
    
    id = Column(BigInteger, primary_key=True)
    formacion_id = Column(BigInteger, nullable=False)
    cargo_id = Column(BigInteger, nullable=False)
    estado = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)

    def __init__(self, data: dict):
        self.formacion_id = data['formacion_id']
        self.cargo_id = data['cargo_id']
        self.created_at = data['created_at']
