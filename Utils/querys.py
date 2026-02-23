import traceback
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
                select n.nit, u.des_usuario as nombre, u.usuario 
                from dbo.negociadores_compras n
                left join usuarios u on n.nit = u.nit
                where n.status = 1 and u.bloqueado is null and u.usuario <> 'MMIRANDA'
                order by u.des_usuario ASC;
            """

            query = self.db.execute(text(sql)).fetchall()
            if query:
                for key in query:
                    response.append({
                        "nit": key.nit,
                        "nombre": key.nombre.upper(),
                        "usuario": key.usuario
                    })

            return response
                
        except Exception as ex:
            print(str(ex))
            raise CustomException(str(ex))
        finally:
            self.db.close()

    # Query para verificar si un usuario es negociador
    def verificar_es_negociador(self, usuario):
        try:
            sql = """
                SELECT COUNT(*) as total
                FROM dbo.negociadores_compras n
                INNER JOIN usuarios u ON n.nit = u.nit
                WHERE u.usuario = :usuario AND n.status = 1;
            """
            result = self.db.execute(text(sql), {"usuario": usuario}).fetchone()
            return result.total > 0 if result else False
                
        except Exception as ex:
            print(str(ex))
            return False
        finally:
            self.db.close()

    # Query para insertar datos de la solicitud.
    def guardar_solicitud(self, data: dict):
        try:
            # Convertir lista de negociadores a string separado por comas
            negociadores_lista = data.get("negociador", [])
            if isinstance(negociadores_lista, list):
                negociadores_str = ",".join(negociadores_lista)
            else:
                negociadores_str = negociadores_lista
            
            sql = """
                INSERT INTO dbo.solicitudes_compras (negociador, asunto, cuerpo_texto, usuario_creador_solicitud, nit_tercero, created_at)
                OUTPUT INSERTED.id
                VALUES (:negociador, :asunto, :cuerpo_texto, :usuario_creador_solicitud, :nit_tercero, :created_at);
            """
            result = self.db.execute(
                text(sql), 
                {
                    "negociador": negociadores_str,
                    "asunto": data["asunto"],
                    "cuerpo_texto": data["cuerpo_texto"],
                    "usuario_creador_solicitud": data["solicitante"],
                    "nit_tercero": data.get("nit_tercero"),
                    "created_at": self.tools.get_colombia_time()
                }
            )
            
            inserted_id = result.scalar()  # PRIMERO capturamos el ID
            self.db.commit()                # LUEGO hacemos commit
            return inserted_id
                
        except Exception as ex:
            print("Error al guardar solicitud:", ex)
            print("Traceback completo:")
            traceback.print_exc()
            self.db.rollback()
            raise CustomException("Error al guardar.")
        finally:
            self.db.close()

    # Query para insertar datos de los detalles de la solicitud.
    def guardar_producto_detalles(self, solicitud_id: int, data: dict):
        try:
            sql = """
                INSERT INTO dbo.solicitudes_compras_detalles (solicitud_id, referencia, producto, 
                cantidad, proveedor, marca, cotizado, created_at) VALUES (:solicitud_id, :referencia, :producto,
                :cantidad, :proveedor, :marca, :cotizado, :created_at);
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
                    "cotizado": data.get("cotizado", 0),  # Valor por defecto 0
                    "created_at": self.tools.get_colombia_time()
                }
            )
            self.db.commit()
                
        except Exception as ex:
            print("Error al guardar producto detalles:", ex)
            print("Traceback completo:")
            traceback.print_exc()
            self.db.rollback()
            raise CustomException("Error al guardar.")
        finally:
            self.db.close()

    # Query para mostrar las solicitudes.
    def mostrar_solicitudes(self, data: dict):
        try:
            solicitud_id = data.get("solicitud_id")
            estado_solicitud = data.get("estado_solicitud")
            solicitante = data.get("solicitante")
            negociador = data.get("negociador")
            fecha_desde = data.get("fecha_desde")
            fecha_hasta = data.get("fecha_hasta")
            cant_registros = 0
            limit = data["limit"]
            position = data["position"]
            result = {"registros": [], "cant_registros": 0}
            response = list()
            
            sql = """
                SELECT COUNT(*) OVER() AS total_registros, 
                    sc.id, sc.negociador, sc.asunto, sc.cuerpo_texto, sc.usuario_creador_solicitud, 
                    sc.estado_solicitud, sc.fecha_resuelto, sc.comentario_resuelto, 
                    sc.porcentaje_solicitud, sc.estado, sc.created_at, sc.nit_tercero,
                    se.nombre as estado_solicitud_nombre,
                    uc.des_usuario as 'usuario_nombre', sc.negociador as 'negociador_nombre',
                    t.nombres as 'tercero_nombre'
                FROM dbo.solicitudes_compras sc
                INNER JOIN dbo.solicitudes_estados se ON sc.estado_solicitud = se.id
                INNER JOIN usuarios uc ON uc.usuario = sc.usuario_creador_solicitud
                LEFT JOIN terceros t ON t.nit = sc.nit_tercero
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
                # Soportar tanto array como string para negociador
                if isinstance(negociador, list) and len(negociador) > 0:
                    # Si es un array de negociadores, buscar que contenga al menos uno
                    conditions = []
                    for idx, neg in enumerate(negociador):
                        param_name = f"negociador_{idx}"
                        conditions.append(f"(sc.negociador LIKE :{param_name} OR sc.negociador LIKE :{param_name}_start OR sc.negociador LIKE :{param_name}_end OR sc.negociador LIKE :{param_name}_middle)")
                        self.query_params.update({
                            f"{param_name}": neg,
                            f"{param_name}_start": f"{neg},%",
                            f"{param_name}_end": f"%,{neg}",
                            f"{param_name}_middle": f"%,{neg},%"
                        })
                    sql += f" AND ({' OR '.join(conditions)})"
                elif negociador:  # Si es un string
                    sql += " AND (sc.negociador LIKE :negociador OR sc.negociador LIKE :negociador_start OR sc.negociador LIKE :negociador_end OR sc.negociador LIKE :negociador_middle)"
                    self.query_params.update({
                        "negociador": negociador,
                        "negociador_start": f"{negociador},%",
                        "negociador_end": f"%,{negociador}",
                        "negociador_middle": f"%,{negociador},%"
                    })
            
            # Filtros de fecha
            if fecha_desde:
                sql += " AND CONVERT(DATE, sc.created_at) >= :fecha_desde"
                self.query_params.update({"fecha_desde": fecha_desde})
            
            if fecha_hasta:
                sql += " AND CONVERT(DATE, sc.created_at) <= :fecha_hasta"
                self.query_params.update({"fecha_hasta": fecha_hasta})
                
            new_offset = self.obtener_limit(limit, position)
            self.query_params.update({"offset": new_offset, "limit": limit})
            sql = sql + " ORDER BY sc.id DESC OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;"

            if self.query_params:
                query = self.db.execute(text(sql), self.query_params).fetchall()
            else:
                query = self.db.execute(text(sql)).fetchall()

            if query:
                cant_registros = query[0].total_registros
            
                # Convertir el resultado a un formato de lista de diccionarios
                response = [
                    {
                        "id": key.id, 
                        "negociador": key.negociador,
                        "asunto": key.asunto,
                        "cuerpo_texto": key.cuerpo_texto,
                        "usuario_creador_solicitud": key.usuario_creador_solicitud,
                        "estado_solicitud": key.estado_solicitud,
                        "fecha_resuelto": str(key.fecha_resuelto) if key.fecha_resuelto else '',
                        "comentario_resuelto": key.comentario_resuelto,
                        "porcentaje_solicitud": key.porcentaje_solicitud,
                        "estado": key.estado,
                        "created_at": self.tools.format_date_flexible(str(key.created_at)) if key.created_at else '',
                        "nit_tercero": key.nit_tercero if key.nit_tercero else '',
                        "estado_solicitud_nombre": key.estado_solicitud_nombre,
                        "usuario_nombre": key.usuario_nombre,
                        "negociador_nombre": self.obtener_nombres_negociadores(key.negociador_nombre) if key.negociador_nombre else '',
                        "tercero_nombre": key.tercero_nombre if key.tercero_nombre else '',
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
                                "id": detalle.id,
                                "referencia": detalle.referencia,
                                "producto": detalle.producto,
                                "cantidad": detalle.cantidad,
                                "proveedor": detalle.proveedor,
                                "marca": detalle.marca,
                                "cotizado": 1 if detalle.cotizado else 0,
                                "negociador": detalle.negociador if detalle.negociador else None
                            } for detalle in detalles_query
                        ] if detalles_query else []
                        
                        # Obtener el historico de la solicitud
                        sql_historico = """
                            SELECT * FROM dbo.solicitudes_compras_detalles_historia WHERE solicitud_id = :solicitud_id;
                        """
                        historico_query = self.db.execute(text(sql_historico), {"solicitud_id": key["id"]}).fetchall()
                        key["historico"] = [
                            {
                                "id": hist.id,
                                "descripcion": hist.descripcion,
                                "fecha": self.tools.format_date_flexible(str(hist.created_at)) if hist.created_at else '',
                            } for hist in historico_query
                        ] if historico_query else []
                        
                result = {"registros": response, "cant_registros": cant_registros}

            return result
                
        except Exception as ex:
            print("Error al mostrar:", ex)
            print("Traceback completo:")
            traceback.print_exc()
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
                        "id": key.id,
                        "nombre": key.nombre
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

    # Función para obtener los nombres de los negociadores desde una lista separada por comas
    def obtener_nombres_negociadores(self, usuarios_str: str):
        try:
            if not usuarios_str:
                return ''
            
            # Separar los usuarios por coma
            usuarios = [u.strip() for u in usuarios_str.split(',')]
            
            # Si solo hay un usuario, obtener su nombre directamente
            if len(usuarios) == 1:
                sql = "SELECT des_usuario FROM usuarios WHERE usuario = :usuario"
                result = self.db.execute(text(sql), {"usuario": usuarios[0]}).fetchone()
                return result.des_usuario.upper() if result else usuarios[0]
            
            # Si hay múltiples usuarios, obtener todos los nombres
            nombres = []
            for usuario in usuarios:
                sql = "SELECT des_usuario FROM usuarios WHERE usuario = :usuario"
                result = self.db.execute(text(sql), {"usuario": usuario}).fetchone()
                if result:
                    nombres.append(result.des_usuario.upper())
                else:
                    nombres.append(usuario)
            
            # Retornar nombres separados por coma
            return ', '.join(nombres)
            
        except Exception as ex:
            print(f"Error al obtener nombres de negociadores: {ex}")
            return usuarios_str  # Retornar el string original si hay error

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
                        "cedula": key.nit,
                        "nombre": key.nombres,
                        "usuario": key.usuario
                    })

            return response
                
        except Exception as ex:
            print(str(ex))
            raise CustomException(str(ex))
        finally:
            self.db.close()

    # Query para obtener los terceros
    def get_terceros(self, busqueda: str = None):

        try:
            response = list()
            
            if busqueda and len(busqueda) >= 3:
                sql = """
                    SELECT TOP 20 * FROM terceros 
                    WHERE nombres LIKE :busqueda OR nit LIKE :busqueda
                    ORDER BY nombres ASC
                """
                query = self.db.execute(text(sql), {"busqueda": f"%{busqueda}%"}).fetchall()
            else:
                # Si no hay búsqueda o es muy corta, retornar lista vacía o primeros 20
                sql = """
                    SELECT TOP 20 * FROM terceros ORDER BY nombres ASC
                """
                query = self.db.execute(text(sql)).fetchall()
            
            if query:
                for key in query:
                    response.append({
                        "nit": key.nit,
                        "nombres": key.nombres
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
                "nombre": query.des_usuario,
                "cedula": str(query.nit),
                "usuario": query.usuario
            })

            return response
                
        except Exception as ex:
            print("Error al login:", str(ex))
            print("Traceback completo:")
            traceback.print_exc()
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

            return query.nit
                
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

            return query.mail
                
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
                    "created_at": self.tools.get_colombia_time()
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
            # Si el estado es 4 (Resuelto) y no viene fecha_resuelto, generarla automáticamente
            fecha_resuelto = data.get("fecha_resuelto")
            if data["nuevo_estado"] == 4 and not fecha_resuelto:
                fecha_resuelto = self.tools.get_colombia_time()
            
            sql = """
                UPDATE dbo.solicitudes_compras
                SET estado_solicitud = :nuevo_estado, fecha_resuelto = :fecha_resuelto, comentario_resuelto = :comentario_resuelto
                WHERE id = :solicitud_id;
            """
            self.db.execute(
                text(sql), 
                {
                    "nuevo_estado": data["nuevo_estado"],
                    "fecha_resuelto": fecha_resuelto,
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
            print("Traceback completo:")
            traceback.print_exc()
            self.db.rollback()
            raise CustomException(str(ex))
        finally:
            self.db.close()

    # Query para actualizar el campo cotizado y negociador de un detalle
    def actualizar_cotizado(self, detalle_id: int, solicitud_id: int, cotizado: int, negociador: str = None):
        try:
            sql = """
                UPDATE dbo.solicitudes_compras_detalles
                SET cotizado = :cotizado, negociador = :negociador
                WHERE id = :detalle_id AND solicitud_id = :solicitud_id AND estado = 1;
            """
            self.db.execute(
                text(sql),
                {
                    "cotizado": cotizado,
                    "negociador": negociador if negociador else None,
                    "detalle_id": detalle_id,
                    "solicitud_id": solicitud_id,
                }
            )
            self.db.commit()

        except CustomException as ex:
            print("Error al actualizar cotizado y negociador:", ex)
            print("Traceback completo:")
            traceback.print_exc()
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
                    "id": key.id,
                    "referencia": key.referencia,
                    "producto": key.producto,
                    "cantidad": key.cantidad,
                    "proveedor": key.proveedor,
                    "marca": key.marca,
                    "producto_despachado": key.producto_despachado,
                    "producto_faltante": key.producto_faltante,
                    "cotizado": 1 if key.cotizado else 0,  # Campo cotizado (BIT) convertido a 1 o 0
                    "negociador": key.negociador if key.negociador else None,  # Campo negociador
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
            
            # Calcular porcentaje de la solicitud basado en items cotizados
            sql_porcentaje = """
                SELECT 
                    COUNT(*) AS total_items,
                    SUM(CASE WHEN cotizado = 1 THEN 1 ELSE 0 END) AS items_cotizados
                FROM dbo.solicitudes_compras_detalles
                WHERE solicitud_id = :solicitud_id AND estado = 1;
            """
            result = self.db.execute(text(sql_porcentaje), {"solicitud_id": solicitud_id}).fetchone()
            
            print("Resultado de la consulta:", result)
            
            porcentaje = 0
            if result and result.total_items:
                print("total_items:", result.total_items)
                print("items_cotizados:", result.items_cotizados)
                total_items = result.total_items
                items_cotizados = result.items_cotizados or 0
                porcentaje = round((items_cotizados / total_items) * 100, 2)
                
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
