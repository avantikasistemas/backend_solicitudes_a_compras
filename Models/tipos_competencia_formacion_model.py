from Config.db import BASE
from sqlalchemy import Column, String, BigInteger, Integer, DateTime
from datetime import datetime

class TiposCompetenciaFormacionModel(BASE):

    __tablename__= "tipos_competencia_formacion"
    
    id = Column(BigInteger, primary_key=True)
    tipo = Column(Integer, nullable=False)
    orden = Column(Integer, nullable=False)
    nombre = Column(String, nullable=False)
    estado = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)
