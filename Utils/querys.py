from Utils.tools import Tools, CustomException
from sqlalchemy import text, or_, case
from sqlalchemy.sql import select
from Models.registro_general_formacion_model import (
    RegistroGeneralFormacionModel as RegistroGeneral
)
from Models.tipo_nivel_formacion_model import TipoNivelFormacionModel
from Models.tipo_actividad_model import TipoActividadModel
from Models.ciudades_formacion_model import CiudadesFormacionModel
from Models.tipos_competencia_formacion_model import TiposCompetenciaFormacionModel
from Models.macroprocesos_model import MacroprocesosModel
from Models.macroprocesos_cargos_model import MacroprocesosCargosModel
from Models.tipo_modalidad_model import TipoModalidadModel
from Models.tipo_estado_formacion_model import TipoEstadoFormacionModel
from Models.tipos_competencia_formacion_detalles_model import TiposCompetenciaFormacionDetalleModel
from Models.macroprocesos_formacion_detalles_model import MacroprocesosFormacionDetalleModel
from Models.cargos_formacion_detalles_model import CargosFormacionDetalleModel
from Models.ciudades_formacion_detalles_model import CiudadesFormacionDetalleModel
from Models.personal_formacion_detalle_model import PersonalFormacionDetalleModel
from Models.tipo_origen_necesidad_model import TipoOrigenNecesidadModel
from Models.tipo_evaluacion_model import TipoEvaluacionModel
from Models.calificaciones_formacion_model import CalificacionesFormacionModel
from collections import defaultdict
import json

class Querys:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()
        self.query_params = dict()

    # Query para obtener los tipos de estado para la cotizacion
    def get_negociadores(self):

        try:
            response = list()
            sql = """
                SELECT DISTINCT u.des_usuario, dph.usuario AS creador_oc
                FROM dbo.documentos_ped_historia AS dph
                INNER JOIN dbo.usuarios AS u ON dph.usuario = u.usuario
                WHERE dph.sw = 3
                AND dph.fecha BETWEEN '20241101' AND '20501231'
                AND dph.bodega <> 99
                AND dph.usuario <> 'JAMARTINEZ'
                ORDER BY u.des_usuario;
            """

            query = self.db.execute(text(sql)).fetchall()
            if query:
                for key in query:
                    response.append({
                        "des_usuario": key[0].upper(),
                        "usuario": key[1]
                    })

            return response
                
        except Exception as ex:
            print(str(ex))
            raise CustomException(str(ex))
        finally:
            self.db.close()
