from pydantic import BaseModel
from typing import Optional

class GuardarFormacion(BaseModel):
    nivel_formacion: int
    tipo_actividad: int
    tema: str
    origen: str
    objetivo_general: str
    objetivo_especifico: str
    modalidad: int
    duracion_horas: Optional[int]
    duracion_minutos: Optional[int]
    metodologia: str
    tipo: int
    proveedor: int
    evaluacion: Optional[str]
    seguimiento: Optional[str]
    fecha_inicio: Optional[str]
    fecha_fin: Optional[str]
