import socket
from Utils.tools import Tools, CustomException
from Utils.querys import Querys
import base64
import pandas as pd
from io import BytesIO

class Solicitud:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()
        self.querys = Querys(self.db)

    # Función para obtener los parametros iniciales
    def guardar_solicitud(self, data: dict):
        """ Api que realiza la consulta de los estados. """
        try:
            correo_solicitante = None
            correo_negociador = None
            mensaje = f"El usuario {data['solicitante']} ha creado una solicitud al negociador {data['negociador']}."

            lista_productos = data["lista_productos"]
            # Verificamos si la lista de productos está vacía
            if not lista_productos:
                raise CustomException("La lista de productos no debe estar vacía.")

            # Guardar la solicitud en la base de datos
            solicitud_id = self.querys.guardar_solicitud(data)

            for producto in lista_productos:
                # Guardar cada producto en la base de datos
                self.querys.guardar_producto_detalles(solicitud_id, producto)
                
            # Guardar historico de creación.
            self.querys.guardar_historico(solicitud_id, mensaje)
                
            correo_solicitante = self.querys.obtener_correo(data["solicitante"])
            correo_negociador = self.querys.obtener_correo(data["negociador"])
                
            # Envío correo de notificación
            self.tools.enviar_correo_notificacion(solicitud_id, data, correo_solicitante, correo_negociador)

            # Retornamos la información.
            return self.tools.output(200, "Solicitud guardada con éxito.")

        except Exception as e:
            print(f"Error al guardar solicitud: {e}")
            raise CustomException("Error al guardar solicitud.")
        
    # Función para consultar los datos de busqueda en modulo CONSULTAR
    def mostrar_solicitudes(self, data: dict):

        try:

            if data["position"] <= 0:
                message = "El campo posición no es válido"
                raise CustomException(message)

            datos_form = self.querys.mostrar_solicitudes(data)

            registros = datos_form["registros"]
            cant_registros = datos_form["cant_registros"]

            if not registros:
                message = "No hay listado de que mostrar."
                return self.tools.output(200, message, data={
                "total_registros": 0,
                "total_pag": 0,
                "posicion_pag": 0,
                "registros": []
            })

            if cant_registros%data["limit"] == 0:
                total_pag = cant_registros//data["limit"]
            else:
                total_pag = cant_registros//data["limit"] + 1

            if total_pag < int(data["position"]):
                message = "La posición excede el número total de registros."
                return self.tools.output(200, message, data={
                "total_registros": 0,
                "total_pag": 0,
                "posicion_pag": 0,
                "registros": []
            })

            registros_dict = {
                "total_registros": cant_registros,
                "total_pag": total_pag,
                "posicion_pag": data["position"],
                "registros": registros
            }

            # Retornamos la información.
            return self.tools.output(200, "Datos encontrados.", registros_dict)

        except Exception as e:
            print(f"Error al obtener información: {e}")
            raise CustomException("Error al obtener información.")

    # Función para actualizar el negociador de la solicitud
    def actualizar_negociador(self, data: dict):
        """ Api que realiza la consulta de los estados. """
        try:
            
            # Mensaje de notificación
            mensaje = f"El usuario {data['usuario_creador']} ha actualizado la solicitud al negociador {data['nuevo_negociador']}."
            
            # Verificamos si la solicitud existe
            self.querys.check_if_solicitud_exists(data["solicitud_id"])

            # Guardar la solicitud en la base de datos
            self.querys.actualizar_negociador(data)

            # Guardar historico de creación.
            self.querys.guardar_historico(data["solicitud_id"], mensaje)

            # Retornamos la información.
            return self.tools.output(200, "Negociador actualizado con éxito.")

        except Exception as e:
            print(f"Error al actualizar negociador: {e}")
            raise CustomException("Error al actualizar negociador.")

    # Función para actualizar el negociador de la solicitud
    def actualizar_estado(self, data: dict):
        """ Api que realiza la consulta de los estados. """
        try:
            
            # Mensaje de notificación
            mensaje = f"El usuario {data['usuario_creador']} ha actualizado el estado de la solicitud a {data['texto_estado']}."
            
            # Verificamos si la solicitud existe
            self.querys.check_if_solicitud_exists(data["solicitud_id"])

            # Guardar la solicitud en la base de datos
            self.querys.actualizar_estado(data)

            # Guardar historico de creación.
            self.querys.guardar_historico(data["solicitud_id"], mensaje)

            # Retornamos la información.
            return self.tools.output(200, "Estado actualizado con éxito.")

        except Exception as e:
            print(f"Error al actualizar estado: {e}")
            raise CustomException("Error al actualizar estado.")

    # Función para cargar el archivo de solicitudes
    def cargar_archivo(self, data: dict):
        """ Api que realiza la consulta de los estados. """
        try:
            
            extensiones_permitidas = ['xlsx']
            
            archivo = data["archivo"]
            nombre = data["nombre"]
            ext = nombre.split(".")[1]

            # Verificamos si el archivo existe
            if not archivo:
                raise CustomException("El archivo no existe.")
            
            # Verificamos si la extensión es válida
            if ext not in extensiones_permitidas:
                raise CustomException("La extensión del archivo no es válida.")
            
            referencias = self.procesar_archivo(archivo)

            # Retornamos la información.
            return self.tools.output(200, "Archivo cargado con éxito.", referencias)

        except CustomException as e:
            print(f"Error al cargar archivo: {e}")
            raise CustomException(str(e))

    # Función para procesar el archivo excel
    def procesar_archivo(self, archivo):
        """ Procesa el archivo de solicitudes. """
        try:
            # 1. Decodificar base64 a binario
            archivo_excel = base64.b64decode(archivo)

            # 2. Convertir binario en archivo legible (BytesIO)
            excel_io = BytesIO(archivo_excel)

            # 3. Leer el archivo con pandas
            df = pd.read_excel(excel_io, engine='openpyxl')

            # 4. Eliminar filas vacías y verificar si hay datos (sin contar cabecera)
            df = df.dropna(how='all')  # Quita filas completamente vacías

            if df.shape[0] == 0:
                raise CustomException("El archivo no contiene datos.")
            
            # Renombrar la columna 'descripcion' a 'producto' si existe
            if 'descripcion' in df.columns:
                df = df.rename(columns={'descripcion': 'producto'})

            # 5. Convertir DataFrame a lista de diccionarios
            data = df.where(pd.notnull(df), None).to_dict(orient='records')

            return data

        except CustomException as e:
            print(f"Error al procesar archivo: {e}")
            raise CustomException(str(e))
