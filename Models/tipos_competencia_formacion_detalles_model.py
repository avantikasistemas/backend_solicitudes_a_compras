from Config.db import BASE
from sqlalchemy import Column, BigInteger, Integer, DateTime
from datetime import datetime

class TiposCompetenciaFormacionDetalleModel(BASE):

    __tablename__= "tipos_competencia_formacion_detalles"
    
    id = Column(BigInteger, primary_key=True)
    formacion_id = Column(BigInteger, nullable=False)
    tipo_competencia_id = Column(BigInteger, nullable=False)
    estado = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)

    def __init__(self, data: dict):
        self.formacion_id = data['formacion_id']
        self.tipo_competencia_id = data['tipo_competencia_id']
        self.created_at = data['created_at']
