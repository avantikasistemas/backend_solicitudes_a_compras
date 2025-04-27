from Utils.tools import Tools, CustomException
from sqlalchemy import text, or_, case
from sqlalchemy.sql import select
from collections import defaultdict
from datetime import datetime

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

    # Query para obtener los tipos de estado para la cotizacion
    # def get_negociadores(self):

    #     try:
    #         response = list()
    #         sql = """
    #             SELECT des_usuario, usuario FROM negociadores;
    #         """

    #         query = self.db.execute(text(sql)).fetchall()
    #         if query:
    #             for key in query:
    #                 response.append({
    #                     "des_usuario": key[0].upper(),
    #                     "usuario": key[1]
    #                 })

    #         return response
                
    #     except Exception as ex:
    #         print(str(ex))
    #         raise CustomException(str(ex))
    #     finally:
    #         self.db.close()

    # Query para insertar datos de la solicitud.
    def guardar_solicitud(self, data: dict):
        try:
            sql = """
                INSERT INTO solicitudes_compras (negociador, cuerpo_texto, usuario_creador_solicitud, created_at)
                VALUES (:negociador, :cuerpo_texto, :usuario_creador_solicitud, :created_at);
            """
            result = self.db.execute(
                text(sql), 
                {
                    "negociador": data["negociador"],
                    "cuerpo_texto": data["cuerpo_texto"],
                    "usuario_creador_solicitud": data["nombre_equipo"],
                    "created_at": datetime.now()
                }
            )
            self.db.commit()

            return result.lastrowid
                
        except Exception as ex:
            print("Error al guardar:", ex)
            self.db.rollback()
            raise CustomException("Error al guardar.")
        finally:
            self.db.close()

    # Query para insertar datos de los detalles de la solicitud.
    def guardar_producto_detalles(self, solicitud_id: int, data: dict):
        try:
            sql = """
                INSERT INTO solicitudes_compras_detalles (solicitud_id, referencia, producto, 
                cantidad, proveedor, marca, created_at) VALUES (:solicitud_id, :referencia, :producto,
                :cantidad, :proveedor, :marca, :created_at);
            """
            self.db.execute(
                text(sql), 
                {
                    "solicitud_id": solicitud_id,
                    "referencia": data["referencia"],
                    "producto": data["producto"],
                    "cantidad": data["cantidad"],
                    "proveedor": data["proveedor"],
                    "marca": data["marca"],
                    "created_at": datetime.now()
                }
            )
            self.db.commit()
                
        except Exception as ex:
            print("Error al guardar:", ex)
            self.db.rollback()
            raise CustomException("Error al guardar.")
        finally:
            self.db.close()

    # Query para mostrar las solicitudes.
    def mostrar_solicitudes(self):
        try:
            sql = """
                SELECT * FROM solicitudes_compras WHERE estado = 1 ORDER BY id DESC;
            """
            query = self.db.execute(text(sql)).fetchall()
            # Convertir el resultado a un formato de lista de diccionarios
            result = [
                {
                    "id": key[0], 
                    "negociador": key[1],
                    "cuerpo_texto": key[2],
                    "usuario_creador_solicitud": key[3],
                    "estado_solicitud": key[4],
                    "estado": key[5],
                    "created_at": str(key[6]),
                } for key in query
            ] if query else []

            if result:
                for key in result:
                    # Obtener los detalles de la solicitud
                    sql_detalles = """
                        SELECT * FROM solicitudes_compras_detalles WHERE solicitud_id = :solicitud_id;
                    """
                    detalles_query = self.db.execute(text(sql_detalles), {"solicitud_id": key["id"]}).fetchall()
                    key["detalles"] = [
                        {
                            "id": detalle[0],
                            "referencia": detalle[2],
                            "producto": detalle[3],
                            "cantidad": detalle[4],
                            "proveedor": detalle[5],
                            "marca": detalle[6]
                        } for detalle in detalles_query
                    ] if detalles_query else []

            return result
                
        except Exception as ex:
            print("Error al mostrar:", ex)
            raise CustomException("Error al mostrar.")
        finally:
            self.db.close()
