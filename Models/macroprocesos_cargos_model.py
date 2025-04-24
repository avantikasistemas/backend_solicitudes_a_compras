from Config.db import BASE
from sqlalchemy import Column, String, BigInteger, Integer, DateTime
from datetime import datetime

class MacroprocesosCargosModel(BASE):

    __tablename__= "macroprocesos_cargos"
    
    id = Column(BigInteger, primary_key=True)
    macroproceso_id = Column(BigInteger)
    cargo_y_personal = Column(String, nullable=True)
    nombre = Column(String, nullable=False)
    estado = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)
