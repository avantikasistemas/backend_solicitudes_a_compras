from Config.db import BASE
from sqlalchemy import Column, String, BigInteger, Integer, DateTime, Date
from datetime import datetime

class RegistroGeneralFormacionModel(BASE):

    __tablename__= "registro_general_formacion"
    
    id = Column(BigInteger, primary_key=True)
    codigo = Column(String, nullable=False)
    nivel_formacion = Column(BigInteger, nullable=False)
    tipo_actividad = Column(BigInteger, nullable=False)
    tema = Column(String, nullable=False)
    origen = Column(String, nullable=False)
    objetivo_general = Column(String, nullable=False)
    objetivo_especifico = Column(String, nullable=False)
    modalidad = Column(BigInteger, nullable=False)
    duracion_horas = Column(Integer, nullable=False)
    duracion_minutos = Column(Integer, nullable=False)
    metodologia = Column(String, nullable=False)
    tipo = Column(BigInteger, nullable=False)
    proveedor = Column(BigInteger, nullable=False)
    evaluacion = Column(String, nullable=False)
    seguimiento = Column(String, nullable=False)
    estado_formacion = Column(BigInteger, nullable=False, default=1)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    estado = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)
    
    def __init__(self, data: dict):
        self.codigo = data['codigo']
        self.nivel_formacion = data['nivel_formacion']
        self.tipo_actividad = data['tipo_actividad']
        self.tema = data['tema']
        self.origen = data['origen']
        self.objetivo_general = data['objetivo_general']
        self.objetivo_especifico = data['objetivo_especifico']
        self.modalidad = data['modalidad']
        self.duracion_horas = data['duracion_horas']
        self.duracion_minutos = data['duracion_minutos']
        self.metodologia = data['metodologia']
        self.tipo = data['tipo']
        self.proveedor = data['proveedor']
        self.evaluacion = data['evaluacion']
        self.seguimiento = data['seguimiento']
        self.estado_formacion = data['estado_formacion']
        self.fecha_inicio = data['fecha_inicio']
        self.fecha_fin = data['fecha_fin']
        self.created_at = data['created_at']
