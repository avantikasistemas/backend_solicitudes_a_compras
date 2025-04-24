from Config.db import BASE
from sqlalchemy import Column, BigInteger, Integer, DateTime, DECIMAL
from datetime import datetime

class PersonalFormacionDetalleModel(BASE):

    __tablename__= "personal_formacion_detalle"
    
    id = Column(BigInteger, primary_key=True)
    formacion_id = Column(BigInteger, nullable=False)
    nit = Column(DECIMAL, nullable=False)
    estado = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)

    def __init__(self, data: dict):
        self.formacion_id = data['formacion_id']
        self.nit = data['nit']
        self.created_at = data['created_at']
