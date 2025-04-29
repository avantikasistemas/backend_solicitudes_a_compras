from Utils.tools import Tools, CustomException
from Utils.querys import Querys

class Parametros:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()
        self.querys = Querys(self.db)
        self.CORPORATIVA = 1
        self.ROL = 2
        self.POSICION = 3

    # Función para obtener los parametros iniciales
    def get_parametros(self):
        """ Api que realiza la consulta de los estados. """

        try:

            # Llamamos a la función de consultar los negociadores
            usuarios = self.querys.get_negociadores()

            # Retornamos la información.
            return self.tools.output(200, "Datos encontrados.", usuarios)

        except Exception as e:
            print(f"Error al obtener información de tercero: {e}")
            raise CustomException("Error al obtener información de tercero.")

    # Función para obtener los estados de la solicitud
    def get_estados_solicitud(self):
        """ Api que realiza la consulta de los estados. """

        try:

            # Llamamos a la función de consultar los estados de la solicitud
            estados = self.querys.get_estados_solicitud()

            # Retornamos la información.
            return self.tools.output(200, "Datos encontrados.", estados)

        except Exception as e:
            print(f"Error al obtener información de tercero: {e}")
            raise CustomException("Error al obtener información de tercero.")

    # Función para obtener personal de cotizaciones
    def get_personal_cotizaciones(self):
        """ Api que realiza la consulta del personal de cotizaciones. """

        try:

            # Llamamos a la función de consultar los estados de la solicitud
            personal = self.querys.get_personal_cotizaciones()

            # Retornamos la información.
            return self.tools.output(200, "Datos encontrados.", personal)

        except Exception as e:
            print(f"Error al obtener información de tercero: {e}")
            raise CustomException("Error al obtener información de tercero.")
