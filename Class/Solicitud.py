import socket
from Utils.tools import Tools, CustomException
from Utils.querys import Querys

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
            correos = list()

            lista_productos = data["lista_productos"]
            # Verificamos si la lista de productos está vacía
            if not lista_productos:
                raise CustomException("La lista de productos no debe estar vacía.")

            # Guardar la solicitud en la base de datos
            solicitud_id = self.querys.guardar_solicitud(data)

            for producto in lista_productos:
                # Guardar cada producto en la base de datos
                self.querys.guardar_producto_detalles(solicitud_id, producto)
                
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
