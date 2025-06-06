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
                SELECT * FROM dbo.v_negociadores_compras ORDER BY des_usuario
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

    # Query para insertar datos de la solicitud.
    def guardar_solicitud(self, data: dict):
        try:
            sql = """
                INSERT INTO dbo.solicitudes_compras (negociador, asunto, cuerpo_texto, usuario_creador_solicitud, created_at)
                OUTPUT INSERTED.id
                VALUES (:negociador, :asunto, :cuerpo_texto, :usuario_creador_solicitud, :created_at);
            """
            result = self.db.execute(
                text(sql), 
                {
                    "negociador": data["negociador"],
                    "asunto": data["asunto"],
                    "cuerpo_texto": data["cuerpo_texto"],
                    "usuario_creador_solicitud": data["solicitante"],
                    "created_at": datetime.now()
                }
            )
            
            inserted_id = result.scalar()  # PRIMERO capturamos el ID
            self.db.commit()                # LUEGO hacemos commit
            return inserted_id
                
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
                INSERT INTO dbo.solicitudes_compras_detalles (solicitud_id, referencia, producto, 
                cantidad, proveedor, marca, producto_faltante, created_at) VALUES (:solicitud_id, :referencia, :producto,
                :cantidad, :proveedor, :marca, :producto_faltante, :created_at);
            """
            self.db.execute(
                text(sql), 
                {
                    "solicitud_id": solicitud_id,
                    "referencia": data["referencia"],
                    "producto": data["producto"],
                    "cantidad": data["cantidad"],
                    "proveedor": data["proveedor"],
                    "producto_faltante": data["cantidad"],
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
    def mostrar_solicitudes(self, data: dict):
        try:
            solicitud_id = data["solicitud_id"]
            estado_solicitud = data["estado_solicitud"]
            solicitante = data["solicitante"]
            negociador = data["negociador"]
            cant_registros = 0
            limit = data["limit"]
            position = data["position"]
            result = {"registros": [], "cant_registros": 0}
            response = list()
            
            sql = """
                SELECT COUNT(*) OVER() AS total_registros, sc.*, se.nombre as estado_solicitud_nombre,
				uc.des_usuario as 'usuario_nombre', u.des_usuario as 'negociador_nombre'
                FROM dbo.solicitudes_compras sc
                INNER JOIN dbo.solicitudes_estados se ON sc.estado_solicitud = se.id
				INNER JOIN usuarios uc ON uc.usuario = sc.usuario_creador_solicitud
				INNER JOIN usuarios u ON u.usuario = sc.negociador
                WHERE sc.estado = 1 AND se.estado = 1
            """
            
            if solicitud_id:
                sql += " AND sc.id = :solicitud_id"
                self.query_params.update({"solicitud_id": solicitud_id})
            
            if estado_solicitud:
                sql += " AND sc.estado_solicitud = :estado_solicitud"
                self.query_params.update({"estado_solicitud": estado_solicitud})

            if solicitante:
                sql += " AND sc.usuario_creador_solicitud = :solicitante"
                self.query_params.update({"solicitante": solicitante})
                
            if negociador:
                sql += " AND sc.negociador = :negociador"
                self.query_params.update({"negociador": negociador})
                
            new_offset = self.obtener_limit(limit, position)
            self.query_params.update({"offset": new_offset, "limit": limit})
            sql = sql + " ORDER BY sc.id DESC OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;"

            if self.query_params:
                query = self.db.execute(text(sql), self.query_params).fetchall()
            else:
                query = self.db.execute(text(sql)).fetchall()

            if query:
                cant_registros = query[0][0]
            
                # Convertir el resultado a un formato de lista de diccionarios
                response = [
                    {
                        "id": key[1], 
                        "negociador": key[2],
                        "asunto": key[3],
                        "cuerpo_texto": key[4],
                        "usuario_creador_solicitud": key[5],
                        "estado_solicitud": key[6],
                        "fecha_resuelto": str(key[7]) if key[7] else '',
                        "comentario_resuelto": key[8],
                        "porcentaje_solicitud": key[9],
                        "estado": key[10],
                        "created_at": self.tools.format_date(str(key[11]), "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S") if str(key[11]) else '',
                        "estado_solicitud_nombre": key[12],
                        "usuario_nombre": key[13],
                        "negociador_nombre": key[14].upper()
                    } for key in query
                ] if query else []

                if response:
                    for key in response:
                        # Obtener los detalles de la solicitud
                        sql_detalles = """
                            SELECT * FROM solicitudes_compras_detalles WHERE solicitud_id = :solicitud_id AND estado = 1;
                        """
                        detalles_query = self.db.execute(text(sql_detalles), {"solicitud_id": key["id"]}).fetchall()
                        key["detalles"] = [
                            {
                                "id": detalle[0],
                                "referencia": detalle[2],
                                "producto": detalle[3],
                                "cantidad": detalle[4],
                                "proveedor": detalle[5],
                                "marca": detalle[6],
                                "producto_despachado": detalle[7],
                                "producto_faltante": detalle[8],
                            } for detalle in detalles_query
                        ] if detalles_query else []
                        
                        # Obtener el historico de la solicitud
                        sql_historico = """
                            SELECT * FROM dbo.solicitudes_compras_detalles_historia WHERE solicitud_id = :solicitud_id;
                        """
                        historico_query = self.db.execute(text(sql_historico), {"solicitud_id": key["id"]}).fetchall()
                        key["historico"] = [
                            {
                                "id": hist[0],
                                "descripcion": hist[2],
                                "fecha": self.tools.format_date(str(hist[4]), "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S") if str(hist[4]) else '',
                            } for hist in historico_query
                        ] if historico_query else []
                        
                result = {"registros": response, "cant_registros": cant_registros}

            return result
                
        except Exception as ex:
            print("Error al mostrar:", ex)
            raise CustomException("Error al mostrar.")
        finally:
            self.db.close()

    # Query para obtener los tipos de estado para la cotizacion
    def get_estados_solicitud(self):

        try:
            response = list()
            sql = """
                SELECT *
                FROM dbo.solicitudes_estados
                WHERE estado = 1
                ORDER BY orden;
            """

            query = self.db.execute(text(sql)).fetchall()
            if query:
                for key in query:
                    response.append({
                        "id": key[0],
                        "nombre": key[2]
                    })

            return response
                
        except Exception as ex:
            print(str(ex))
            raise CustomException(str(ex))
        finally:
            self.db.close()

    # Función para obtener el limite de para paginar
    def obtener_limit(self, limit: int, position: int):
        offset = (position - 1) * limit
        return offset

    # Query para obtener los tipos de estado para la cotizacion
    def get_personal_cotizaciones(self):

        try:
            response = list()
            sql = """
                SELECT va.nit, va.nombres, u.usuario
                FROM v_personal_activo va
                INNER JOIN usuarios u ON u.nit = va.nit
                WHERE va.descripcion IN ('ASESOR DE VENTA', 'ASESOR DE VENTAS TELEMERCADEO', 'COORDINADOR DE COTIZACIONES')
                AND u.bloqueado IS NULL
                ORDER BY va.nombres ASC
            """

            query = self.db.execute(text(sql)).fetchall()
            if query:
                for key in query:
                    response.append({
                        "cedula": key[0],
                        "nombre": key[1],
                        "usuario": key[2]
                    })

            return response
                
        except Exception as ex:
            print(str(ex))
            raise CustomException(str(ex))
        finally:
            self.db.close()

    # Query para obtener la informacion del usuario
    def get_usuario(self, usuario, password):

        try:
            response = dict()
            sql = """
                SELECT des_usuario, nit, usuario
                FROM dbo.usuarios
                WHERE usuario = :usuario
                AND clave = :clave;
            """

            query = self.db.execute(
                text(sql), 
                {"usuario": usuario, "clave": password}
            ).fetchone()
            if not query:
                raise CustomException("Usuario o contraseña incorrecta.")
            
            response.update({
                "nombre": query[0],
                "cedula": str(query[1]),
                "usuario": query[2]
            })

            return response
                
        except Exception as ex:
            print(str(ex))
            raise CustomException("Error al intentar conectar con la base de datos.")
        finally:
            self.db.close()

    # Query para obtener los datos de usuario por cedula, esta query solo es
    # usada para validacion del jwt bearer
    def get_usuario_x_cedula(self, cedula):

        try:
            sql = """
                SELECT nit
                FROM dbo.usuarios
                WHERE nit = :cedula;
            """

            query = self.db.execute(text(sql), {"cedula": cedula}).fetchone()

            return query[0]
                
        except Exception as ex:
            print(str(ex))
            raise CustomException(str(ex))
        finally:
            self.db.close()

    # Consulta para traer el correo electrónico del usuario.
    def obtener_correo(self, usuario):

        try:
            sql = """
                select t.mail
                from usuarios u
                inner join terceros t on t.nit = u.nit
                where u.usuario = :usuario
            """

            query = self.db.execute(text(sql), {"usuario": usuario}).fetchone()

            return query[0]
                
        except Exception as ex:
            print(str(ex))
            raise CustomException(str(ex))
        finally:
            self.db.close()

    # Query para guardar historico de la solicitud
    def guardar_historico(self, solicitud_id: int, mensaje: str):
        try:
            sql = """
                INSERT INTO dbo.solicitudes_compras_detalles_historia (solicitud_id, descripcion, created_at)
                VALUES (:solicitud_id, :descripcion, :created_at);
            """
            self.db.execute(
                text(sql), 
                {
                    "solicitud_id": solicitud_id,
                    "descripcion": mensaje,
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

    # Query para verificar si la solicitud existe
    def check_if_solicitud_exists(self, solicitud_id: int):
        try:
            sql = """
                SELECT COUNT(*) FROM dbo.solicitudes_compras WHERE id = :solicitud_id;
            """
            result = self.db.execute(text(sql), {"solicitud_id": solicitud_id}).scalar()
            if result == 0:
                raise CustomException("La solicitud no existe.")
                
        except Exception as ex:
            print(str(ex))
            raise CustomException(str(ex))
        finally:
            self.db.close()

    # Query para actualizar el negociador de la solicitud
    def actualizar_negociador(self, data: dict):
        try:
            sql = """
                UPDATE dbo.solicitudes_compras
                SET negociador = :nuevo_negociador
                WHERE id = :solicitud_id;
            """
            self.db.execute(
                text(sql), 
                {
                    "nuevo_negociador": data["nuevo_negociador"],
                    "solicitud_id": data["solicitud_id"]
                }
            )
            self.db.commit()
                
        except Exception as ex:
            print("Error al actualizar negociador:", ex)
            self.db.rollback()
            raise CustomException("Error al actualizar negociador.")
        finally:
            self.db.close()

    # Query para actualizar el estado de la solicitud
    def actualizar_estado(self, data: dict):
        try:
            sql = """
                UPDATE dbo.solicitudes_compras
                SET estado_solicitud = :nuevo_estado, fecha_resuelto = :fecha_resuelto, comentario_resuelto = :comentario_resuelto
                WHERE id = :solicitud_id;
            """
            self.db.execute(
                text(sql), 
                {
                    "nuevo_estado": data["nuevo_estado"],
                    "fecha_resuelto": data["fecha_resuelto"],
                    "comentario_resuelto": data["comentario_resuelto"],
                    "solicitud_id": data["solicitud_id"]
                }
            )
            self.db.commit()
                
        except Exception as ex:
            print("Error al actualizar estado:", ex)
            self.db.rollback()
            raise CustomException("Error al actualizar estado.")
        finally:
            self.db.close()

    # Query para actualizar la cantidad de un detalle de la solicitud
    def actualizar_cantidad_detalle(self, data: dict):
        try:
            
            detalle_id = data["detalle_id"]
            cantidad_nueva = data["cantidad_nueva"]
            solicitud_id = data["solicitud_id"]
            producto_despachado = data["producto_despachado"]
            producto_faltante = data["producto_faltante"]
            
            if cantidad_nueva > producto_faltante:
                raise CustomException("La cantidad nueva no puede ser mayor a la cantidad faltante.")
            
            producto_despachado = producto_despachado + cantidad_nueva
            producto_faltante = producto_faltante - cantidad_nueva
            if producto_faltante < 0:
                producto_faltante = 0
                
            sql = """
                UPDATE dbo.solicitudes_compras_detalles
                SET producto_despachado = :producto_despachado, producto_faltante = :producto_faltante
                WHERE id = :detalle_id AND solicitud_id = :solicitud_id AND estado = 1;
            """
            self.db.execute(
                text(sql),
                {
                    "producto_despachado": producto_despachado,
                    "producto_faltante": producto_faltante,
                    "detalle_id": detalle_id,
                    "solicitud_id": solicitud_id,
                }
            )
            self.db.commit()

        except CustomException as ex:
            print("Error al actualizar cantidad detalle:", ex)
            self.db.rollback()
            raise CustomException(str(ex))
        finally:
            self.db.close()

    # Query para cargar los detalles de la solicitud
    def get_detalles_solicitud(self, data: dict):
        try:
            sql = """
                SELECT * FROM dbo.solicitudes_compras_detalles
                WHERE solicitud_id = :solicitud_id AND estado = 1;
            """
            result = self.db.execute(text(sql), {"solicitud_id": data["solicitud_id"]}).fetchall()
            return [
                {
                    "id": key[0],
                    "referencia": key[2],
                    "producto": key[3],
                    "cantidad": key[4],
                    "proveedor": key[5],
                    "marca": key[6],
                    "producto_despachado": key[7],
                    "producto_faltante": key[8],
                } for key in result
            ] if result else []

        except Exception as ex:
            print("Error al obtener detalles de la solicitud:", ex)
            raise CustomException("Error al obtener detalles de la solicitud.")
        finally:
            self.db.close()

    # Query pra actualizar el porcentaje de avance de la solicitud
    def actualizar_porcentaje(self, solicitud_id: int):
        try:
            
            # Calcular porcentaje de la solicitud
            sql_porcentaje = """
                SELECT 
                    SUM(cantidad) AS total_cantidad,
                    SUM(producto_despachado) AS total_despachado
                FROM dbo.solicitudes_compras_detalles
                WHERE solicitud_id = :solicitud_id AND estado = 1;
            """
            result = self.db.execute(text(sql_porcentaje), {"solicitud_id": solicitud_id}).fetchone()
            
            print("Resultado de la consulta:", result)
            
            porcentaje = 0
            if result and result[0]:
                print("total_cantidad:", result[0])
                print("total_despachado:", result[1])
                total_cantidad = result[0]
                total_despachado = result[1] or 0
                porcentaje = round((total_despachado / total_cantidad) * 100, 2)
                
            print("Porcentaje calculado:", porcentaje)
                
            # Actualizar el porcentaje en la cabecera
            sql_update_cabecera = """
                UPDATE dbo.solicitudes_compras
                SET porcentaje_solicitud = :porcentaje
                WHERE id = :solicitud_id;
            """

            self.db.execute(
                text(sql_update_cabecera),
                {"porcentaje": porcentaje, "solicitud_id": solicitud_id}
            )
            self.db.commit()


        except Exception as ex:
            print("Error al actualizar porcentaje:", ex)
            self.db.rollback()
            raise CustomException("Error al actualizar porcentaje.")
        finally:
            self.db.close()
