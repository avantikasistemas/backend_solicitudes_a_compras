from Config.db import BASE
from sqlalchemy import Column, String, BigInteger, Integer, DateTime
from datetime import datetime

class MacroprocesosModel(BASE):

    __tablename__= "macroprocesos"
    
    id = Column(BigInteger, primary_key=True)
    codigo = Column(String, nullable=False)
    nombre = Column(String, nullable=False)
    estado = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)
