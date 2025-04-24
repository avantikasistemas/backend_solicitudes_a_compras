from Config.db import BASE
from sqlalchemy import Column, String, BigInteger, Integer, DateTime, DECIMAL
from datetime import datetime

class CalificacionesFormacionModel(BASE):

    __tablename__= "calificaciones_formacion"
    
    id = Column(BigInteger, primary_key=True)
    formacion_id = Column(BigInteger)
    cedula = Column(DECIMAL(18, 0), nullable=False)
    nota_eva_escrita = Column(DECIMAL(5, 2), nullable=True, default=None)
    nota_eva_practica = Column(DECIMAL(5, 2), nullable=True, default=None)
    nota_eva_interactiva = Column(DECIMAL(5, 2), nullable=True, default=None)
    estado = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)
    
    def __init__(self, data: dict):
        self.formacion_id = data['formacion_id']
        self.cedula = data['cedula']
        self.nota_eva_escrita = data['nota_eva_escrita']
        self.nota_eva_practica = data['nota_eva_practica']
        self.nota_eva_interactiva = data['nota_eva_interactiva']
        self.created_at = data['created_at']
