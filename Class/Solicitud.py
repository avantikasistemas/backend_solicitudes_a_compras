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

            lista_productos = data["lista_productos"]
            # Verificamos si la lista de productos está vacía
            if not lista_productos:
                raise CustomException("La lista de productos no debe estar vacía.")

            # Obtener el nombre del equipo
            nombre_equipo = socket.gethostname()
            
            # Agregar el nombre del equipo a data
            data['nombre_equipo'] = nombre_equipo

            # Guardar la solicitud en la base de datos
            solicitud_id = self.querys.guardar_solicitud(data)

            for producto in lista_productos:
                # Guardar cada producto en la base de datos
                self.querys.guardar_producto_detalles(solicitud_id, producto)

            # Retornamos la información.
            return self.tools.output(200, "Solicitud guardada con éxito.")

        except Exception as e:
            print(f"Error al guardar solicitud: {e}")
            raise CustomException("Error al guardar solicitud.")

    # Función para obtener los parametros iniciales
    def mostrar_solicitudes(self):
        """ Api que realiza la consulta de los estados. """
        try:

            lista_solicitudes = self.querys.mostrar_solicitudes()

            # Retornamos la información.
            return self.tools.output(200, "Datos encontrados.", lista_solicitudes)

        except Exception as e:
            print(f"Error al guardar solicitud: {e}")
            raise CustomException("Error al guardar solicitud.")
